from django.urls import include, path, re_path

from . import views

app_name = 'api'
urlpatterns = [
    path('', views.HelloBio3science.as_view(), name='index'),
    path('account', views.AccountList.as_view(), name='user-list'),
    path('account/<int:pk>', views.AccountDetail.as_view(), name='user-detail'),
    path('place/<str:input_search>', views.Place.as_view(), name='place'),
    # path('email-disponible/<str:email>', views.AccountByEmail.as_view(), name='email-disponible'),
    path('degree', views.DegreeList.as_view(), name='degree-list'),
    path('fields-of-study', views.FieldsOfStudyList.as_view(), name='fields-of-study-list'),
    path('profile', views.ProfileList.as_view(), name='profile-list'),
    path('university', views.UniversityList.as_view(), name='university-list'),
    path('university/<int:pk>', views.UniversityDetail.as_view(), name='university-detail'),
    path('generate-token-reset-password', views.GenerateTokenResetPassword.as_view(), name='generate-token-reset-password'),
    path('project', views.ProjectList.as_view(), name='project-list'),
    path('project/<int:pk>', views.ProjectDetail.as_view(), name='project-detail'),
    path('community', views.CommunityList.as_view(), name='community-list'),
    path('project-image', views.ProjectImageList.as_view(), name='project-image'),
    path('project-network', views.ProjectNetworkList.as_view(), name='project-network'),
    path('project-network-expanded', views.ProjectNetworkExpandedList.as_view(), name='project-network-expanded'),
    path('project-network-expanded/<int:pk>', views.ProjectNetworkExpandedDetail.as_view(), name='project-network-expanded-detail'),
    path('nodes-network', views.NodesNetworkList.as_view(), name='nodes-network'),
    path('nodes-network/<int:pk>', views.NodesNetworkDetail.as_view(), name='nodes-network-detail'),
    path('project-expanded', views.ProjectExpandedList.as_view(), name='project-expanded'),
    path('project-expanded/<int:pk>', views.ProjectExpandedDetail.as_view(), name='project-expanded-detail'),
    path('profile/<int:pk>', views.ProfileDetail.as_view(), name='profile-detail'),

]