import requests
from django.db.models import F
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from .models import CustomUser as User
from .models import FriendsRelationship, FriendsRequest
from .serializers import (CoordinateSerializer, CustomUserSerializer,
                          FriendSerializer, FriendsRelationshipSerializer,
                          UserpicSerializer, UserStatusSerializer)


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для работы с пользователем."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("tags",)
    search_fields = ("^email", "^username", "^first_name", "^last_name")

    @action(detail=False)
    def friends(self, request):
        query_param = self.request.GET.get('friends_category')
        if query_param:
            friends = request.user.friends.filter(
                friend__friend_category=query_param
            ).annotate(friend_category=F('friend__friend_category'))
        else:
            friends = request.user.friends.all().annotate(
                friend_category=F('friend__friend_category')
            )
        serializer = FriendSerializer(
            friends, many=True, context={"request": request}
        )
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="add-friend",
    )
    def add_friend(self, request, **kwargs):
        from_user = request.user
        to_user = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = FriendSerializer(
            to_user, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        if FriendsRequest.objects.filter(
            from_user=to_user, to_user=from_user
        ).exists():
            FriendsRequest.objects.filter(
                from_user=to_user, to_user=from_user
            ).delete()
            from_user.friends.add(to_user)
        else:
            FriendsRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="approved",
    )
    def approve_request(self, request, **kwargs):
        to_user = request.user
        from_user = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = FriendSerializer(
            from_user, data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        if not FriendsRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists():
            return Response(
                {"errors": "Такой заявки нет."}, status=HTTP_400_BAD_REQUEST
            )
        FriendsRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).delete()
        from_user.friends.add(to_user)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=["delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="delete-friend",
    )
    def delete_friend(self, request, **kwargs):
        current_user = request.user
        friend = get_object_or_404(User, id=self.kwargs.get("id"))
        if not FriendsRelationship.objects.filter(
            current_user=current_user, friend=friend
        ).exists():
            return Response(
                {"errors": "Пользователя нет в друзьях."},
                status=HTTP_400_BAD_REQUEST,
            )
        current_user.friends.remove(friend)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=["delete"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="delete-request",
    )
    def delete_request(self, request, **kwargs):
        from_user = request.user
        to_user = get_object_or_404(User, id=self.kwargs.get("id"))
        if not FriendsRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).exists():
            return Response(
                {"errors": "Такой заявки не существует."},
                status=HTTP_400_BAD_REQUEST,
            )
        FriendsRequest.objects.filter(
            from_user=from_user, to_user=to_user
        ).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="all-requests",
    )
    def all_requests(self, request):
        all_requests = User.objects.filter(user__to_user=request.user)
        serializer = FriendSerializer(
            all_requests, many=True, context={"request": request}
        )
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        methods=["patch"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="update-coordinates",
    )
    def update_coordinates(self, request, **kwargs):
        user = get_object_or_404(User, id=self.kwargs.get("id"))
        serializer = CoordinateSerializer(
            user,
            partial=True,
            data=self.request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(
                data=serializer.errors, status=HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path="get-friends",
    )
    def get_friends(self, request, **kwargs):
        friends = request.user.friends.all()
        nearby_friends = friends.filter(
            longitude__gte=self.request.data["start_longitude"],
            longitude__lte=self.request.data["end_longitude"],
            latitude__gte=self.request.data["start_latitude"],
            latitude__lte=self.request.data["end_latitude"],
        )
        serializer = FriendSerializer(
            data=nearby_friends,
            many=True,
            context={"request": request},
        )
        serializer.is_valid()
        if len(serializer.data) == 0:
            return Response(serializer.data, status=HTTP_204_NO_CONTENT)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        methods=["patch"],
        detail=True,
        url_path="update-friends-category",
    )
    def update_friends_category(self, request, **kwargs):
        current_user = request.user
        friend = get_object_or_404(User, id=self.kwargs.get("id"))
        friendship_bond = FriendsRelationship.objects.get(
            current_user=current_user,
            friend=friend
        )
        serializer = FriendsRelationshipSerializer(
            friendship_bond,
            partial=True,
            data=self.request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(
                {"Fail": "Передано некорректное наименование категории"},
                status=HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=["patch"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="update-user-pic",
    )
    def update_user_pic(self, request, **kwargs):
        user = request.user
        serializer = UserpicSerializer(
            user,
            partial=True,
            data=self.request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(
                data=serializer.errors, status=HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    @action(
        methods=["patch"],
        detail=True,
        url_path="update-user-status",
    )
    def update_user_status(self, request, **kwargs):
        serializer = UserStatusSerializer(
            request.user,
            partial=True,
            data=self.request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return Response(
                data=serializer.errors, status=HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)


class ActivateUserView(GenericAPIView):
    """Подтверждение мейла."""

    permission_classes = [AllowAny]

    def get(self, request, uid, token, format=None):
        """Отправка POST вместо GET."""
        payload = {"uid": uid, "token": token}
        actiavtion_url = settings.ACTIVATION_URL
        response = requests.post(actiavtion_url, data=payload)
        if response.status_code == 204:
            return HttpResponseRedirect(redirect_to=settings.LOGIN_URL_)
        return Response(response.json())
