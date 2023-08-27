from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from api.views import TagViewSet
from users.views import ActivateUserView, CustomUserViewSet
from places.views import PlacesViewSet

app_name = "api"

openapi_info = openapi.Info(
    title='"Where are my friends?" API',
    default_version="v1",
    description=(
        "Specification for the backend "
        'project application "Where are my friends?"'
    ),
    license=openapi.License(name="BSD License"),
)
schema_view = get_schema_view(
    openapi_info,
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("users", CustomUserViewSet)
router.register("users/(?P<user_id>[1-9][0-9]*)/places", PlacesViewSet)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/", include("djoser.urls")),
    path("v1/", include("djoser.urls.jwt")),
    path("account-activate/<uid>/<token>/", ActivateUserView.as_view()),
]


urlpatterns += [
    re_path(
        r"^v1/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "v1/swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "v1/redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
