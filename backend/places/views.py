from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Place, SharedPlaces
from .permissions import IsAuthor
from .serializers import PlacesSerializer, SharingSerializer


class PlacesViewSet(viewsets.ModelViewSet):
    """CRUD для пользовательских мест."""

    queryset = Place.objects.all()
    serializer_class = PlacesSerializer
    permission_classes = (IsAuthor,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["post"],
        detail=True,
        url_path="share-place",
    )
    def share_place(self, request, **kwargs):
        sharing_place = self.kwargs.get("pk")
        sharing_to_user = request.data.get("sharing_to_user")
        data = {
            "sharing_place": sharing_place,
            "sharing_to_user": sharing_to_user,
        }
        serializer = SharingSerializer(data=data, context={"request": request})

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(sharing_user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=["delete"],
        detail=True,
        url_path="stop-sharing-place",
    )
    def stop_sharing_place(self, request, **kwargs):
        sharing_place = self.kwargs.get("pk")
        sharing_to_user = request.data.get("sharing_to_user")

        place = SharedPlaces.objects.filter(
            sharing_place=sharing_place,
            sharing_to_user=sharing_to_user,
            sharing_user=self.request.user,
        )

        if not place.exists():
            return Response(
                {"errors": "Такое место не шарится этому человеку."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        place.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=["get"],
        detail=False,
        url_path="all-shared-places",
    )
    def all_shared_places(self, request, user_id):
        all_requests = SharedPlaces.objects.filter(
            sharing_user=self.request.user
        )
        serializer = SharingSerializer(
            all_requests, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
