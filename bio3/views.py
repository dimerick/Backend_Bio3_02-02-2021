from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CustomUser, Profile, University, Degree, FieldsOfStudy, Project, Community, ProjectImage
from .serializers import CustomUserSerializer, ProfileSerializer, UniversitySerializer, DegreeSerializer, ProjectSerializer, CommunitySerializer, ProjectImageSerializer
from django.http import Http404
import googlemaps
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db import connection
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import BasePermission

# Create your views here.

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `created_by_id`.
        print(request.user)
        return obj.created_by_id == request.user.id

class HelloBio3science(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


    def get(self, request):
        content = {"message": "Alersnet Rocking"}
        return Response(content)

class Place(APIView):
    #permission_classes = [permissions.IsAuthenticated]


    def get(self, request, input_search):

        gmaps = googlemaps.Client(key=settings.GOOGLE_KEY)

        #input_search = request.get['input_search']

        #result = gmaps.find_place(input_search, 'textquery', ['business_status', 'formatted_address', 'geometry', 'icon', 'name', 'photos', 'place_id', 'plus_code', 'types'])

        result = gmaps.places_autocomplete_query(input_search, 3)

        return Response(result)

class AccountList(APIView):

    def get(self, request, format=None):

        email = request.GET.get('email', None)
        if(email):
            objs = CustomUser.objects.filter(email=email)
        else:
            objs = CustomUser.objects.all()
            
        serializer = CustomUserSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class AccountDetail(APIView):  

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    def get(self, request, pk=None, format=None):

        
        obj = self.get_object(pk)
        
        serializer = CustomUserSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CustomUserSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class AccountByEmail(APIView):
        
#     def get(self, request, email, format=None):
#         user = get_object_by_email(email)
#         serializer = CustomUserSerializer(user)
#         return Response(serializer.data)

class ProfileList(APIView):

    def get(self, request, format=None):
        objs = Profile.objects.all()
        serializer = ProfileSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniversityList(APIView):

    def get(self, request, format=None):

        user = request.GET.get('user', None)
        exclude_id = request.GET.get('exclude_id', None)
        tipo = request.GET.get('tipo', None)
        
        if user:
            with connection.cursor() as cursor:
                cursor.execute("select uni.id, uni.name, ST_Y(uni.location) as lat, ST_X(uni.location) as lon, created_at, uni.created_by_id as created_by, tipo from bio3_university uni where tipo = %s and uni.id <> %s union all select uni.id, 'My Location' as name, ST_Y(uni.location) as lat, ST_X(uni.location) as lon, created_at, uni.created_by_id as created_by, tipo from bio3_university uni inner join bio3_profile prof on uni.id = prof.university_id where prof.user_id = %s;", [tipo, exclude_id, user])
                unis_tmp = dictfetchall(cursor)
                print(str(len(unis_tmp)))
                universities = []
                for i in range(0, len(unis_tmp)):
                    universities.append({'id': unis_tmp[i]['id'], 'projects': [], 'name': unis_tmp[i]['name'], 'location': {'type': 'Point', 'coordinates': [unis_tmp[i]['lon'], unis_tmp[i]['lat']]}, 'created_at': unis_tmp[i]['created_at'], 'tipo': unis_tmp[i]['tipo'], 'created_by': unis_tmp[i]['created_by']})
                
            return JsonResponse(universities, safe=False)
        else:
            name = request.GET.get('name', None)
            exclude_id = request.GET.get('exclude_id', None)
            if(name):
                objs = University.objects.filter(name__icontains=name, tipo=tipo).exclude(id=exclude_id)
            else:
                objs = University.objects.filter(tipo=tipo).exclude(id=exclude_id)

            serializer = UniversitySerializer(objs, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = UniversitySerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniversityDetail(APIView):    

    def get_object(self, pk):
        try:
            return University.objects.get(id=pk)
        except University.DoesNotExist:
            raise Http404

    
    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = UniversitySerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)

        # created_by = request.GET.get('created_by', None)
        # if(created_by):
        #     obj.created_by = CustomUser.objects.get(id=created_by)
        #     obj.save()
        #     serializer = UniversitySerializer(data=obj)
        #     if serializer.is_valid():
        #         return Response(serializer.data)

        serializer = UniversitySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DegreeList(APIView):

    def get(self, request, format=None):
        degrees = Degree.objects.all()
        serializer = DegreeSerializer(degrees, many=True)
        return Response(serializer.data)

class FieldsOfStudyList(APIView):

    def get(self, request, format=None):
        items = FieldsOfStudy.objects.all()
        serializer = DegreeSerializer(items, many=True)
        return Response(serializer.data)

class GenerateTokenResetPassword(APIView):

    def get_object(self, email):
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request):
        email = request.GET.get('email', None)
        obj = self.get_object(email)
        token = default_token_generator.make_token(obj)
        print(token)



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        user.last_login = timezone.now()
        user.save()
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ProjectList(APIView):

    def get(self, request, format=None):

        name = request.GET.get('name', None)
        user = request.GET.get('user', None)
        if(user):
            objs = Project.objects.filter(created_by_id=user, is_active=True).order_by('-created_at')
        elif(name):
            objs = Project.objects.filter(name__icontains=name, is_active=True).order_by('-created_at')
        else:
            objs = Project.objects.all().filter(is_active=True).order_by('-created_at')

        
        serializer = ProjectSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(APIView):

    # serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            obj = Project.objects.get(id=pk, is_active=True)
            self.check_object_permissions(self.request, obj)
            return obj
        except Project.DoesNotExist:
            raise Http404

    
    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectImageList(APIView):

    def get(self, request, format=None):

        project = request.GET.get('project', None)
        if(project):
            objs = ProjectImage.objects.filter(project=project)
        else:
            objs = ProjectImage.objects.all()

        serializer = ProjectImageSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectImageSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityList(APIView):

    def get(self, request, format=None):
        objs = Community.objects.all()
        serializer = CommunitySerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommunitySerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommunityDetail(APIView):    

    def get_object(self, pk):
        try:
            return Community.objects.get(id=pk)
        except Community.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CommunitySerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CommunitySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

class ProjectNetworkList(APIView):
    
    def get(self, request, format=None):
        with connection.cursor() as cursor:
            cursor.execute("select project.id, project.name, project.description, project.created_at, uni.name as universidad, ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_AsText(ST_Transform(uni.location, 4326)) as uni_location, user2.id as user_id, user2.name as user_name, user2.last_name as user_last_name from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_customuser user2 on project.created_by_id = user2.id where project.is_active = true;")
            projects = dictfetchall(cursor)
            for i in range(0, len(projects)):
                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(uni_assoc.location) as long_assoc, ST_Y(uni_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni_assoc on pu.university_id = uni_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['universities_network'] = dictfetchall(cursor)

                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(community_assoc.location) as long_assoc, ST_Y(community_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_communities pc on project.id = pc.project_id inner join bio3_community community_assoc on pc.community_id = community_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['communities_network'] = dictfetchall(cursor)

                cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, projects[i]['id']])
                projects[i]['images'] = dictfetchall(cursor)

            return JsonResponse(projects, safe=False)

class NodesNetworkList(APIView):
    def get(self, request, format=None):
        nodes = dict()
        search = request.GET.get('search', None)

        if(search):
            search = '%' + search + '%'
            with connection.cursor() as cursor:
                cursor.execute("select uni.id, min(uni.name) as name, min(uni.long) as long, min(uni.lat) as lat, 10+exp(sum(uni.points)*0.001) as points from (select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*1 as points from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id where project.is_active = true and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s) group by uni.id union all select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*0.5 as points from bio3_project project inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni on pu.university_id = uni.id where project.is_active = true and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s) group by university_id) as uni group by uni.id;", [search, search, search, search])
                nodes['universities'] = dictfetchall(cursor)
        
            with connection.cursor() as cursor2:
                cursor2.execute("select pc.community_id as id, min(community.name) as name, min(ST_X(community.location)) as long, min(ST_Y(community.location)) as lat, 10+exp((count(pc.community_id) * 0.5)*0.001) as points from bio3_project_communities pc inner join bio3_project project on pc.project_id = project.id inner join bio3_community community on pc.community_id = community.id where project.is_active = true and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s) group by pc.community_id;", [search, search])
                nodes['communities'] = dictfetchall(cursor2)
        else:
            with connection.cursor() as cursor:
                cursor.execute("select uni.id, min(uni.name) as name, min(uni.long) as long, min(uni.lat) as lat, 10+exp(sum(uni.points)*0.001) as points from (select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*1 as points from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id where project.is_active = true group by uni.id union all select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*0.5 as points from bio3_project project inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni on pu.university_id = uni.id where project.is_active = true group by university_id) as uni group by uni.id;")
                nodes['universities'] = dictfetchall(cursor)
        
            with connection.cursor() as cursor2:
                cursor2.execute("select pc.community_id as id, min(community.name) as name, min(ST_X(community.location)) as long, min(ST_Y(community.location)) as lat, 10+exp((count(pc.community_id) * 0.5)*0.001) as points from bio3_project_communities pc inner join bio3_project project on pc.project_id = project.id inner join bio3_community community on pc.community_id = community.id where project.is_active = true group by pc.community_id;")
                nodes['communities'] = dictfetchall(cursor2)
        return JsonResponse(nodes, safe=False)

class NodesNetworkDetail(APIView):

    def get_object(self, pk):
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):

        obj = self.get_object(pk)
        nodes = dict()
        with connection.cursor() as cursor:
            cursor.execute("select uni.id, min(uni.name) as name, min(uni.long) as long, min(uni.lat) as lat, 10+exp(sum(uni.points)*0.001) as points from (select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*1 as points from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id where project.id = %s and project.is_active = true group by uni.id union all select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*0.5 as points from bio3_project project inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni on pu.university_id = uni.id where project.id = %s and project.is_active = true group by university_id) as uni group by uni.id;", [obj.id, obj.id])
            nodes['universities'] = dictfetchall(cursor)
        
        with connection.cursor() as cursor2:
            cursor2.execute("select pc.community_id as id, min(community.name) as name, min(ST_X(community.location)) as long, min(ST_Y(community.location)) as lat, 10+exp((count(pc.community_id) * 0.5)*0.001) as points from bio3_project_communities pc inner join bio3_project project on pc.project_id = project.id inner join bio3_community community on pc.community_id = community.id where project.id = %s and project.is_active = true group by pc.community_id;", [obj.id])
            nodes['communities'] = dictfetchall(cursor2)
        return JsonResponse(nodes, safe=False)

class ProjectExpandedList(APIView):
    
    def get(self, request, format=None):

        user = request.GET.get('user', None)

        with connection.cursor() as cursor:
            if user:
                cursor.execute("select project.id, project.name, project.description, project.created_at, project.main_university_id as main_university, uni.name as universidad, ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_AsText(ST_Transform(uni.location, 4326)) as uni_location, user2.id as user_id, user2.name as user_name, user2.last_name as user_last_name from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_customuser user2 on project.created_by_id = user2.id where project.is_active = true and project.created_by_id = %s order by project.created_at desc;", [user])
            else:
                cursor.execute("select project.id, project.name, project.description, project.created_at, project.main_university_id as main_university, uni.name as universidad, ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_AsText(ST_Transform(uni.location, 4326)) as uni_location, user2.id as user_id, user2.name as user_name, user2.last_name as user_last_name from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_customuser user2 on project.created_by_id = user2.id where project.is_active = true order by project.created_at desc;")
            projects = dictfetchall(cursor)

            for i in range(0, len(projects)):
                projects[i]['name_uni'] = projects[i]['name']+' - '+projects[i]['universidad']
                cursor.execute("select university_id from bio3_project_universities where project_id = %s;", [projects[i]['id']])
                universities = dictfetchall(cursor)
                projects[i]['universities'] = []
                for j in range(0, len(universities)):
                    projects[i]['universities'].append(universities[j]['university_id'])
                
                cursor.execute("select community_id from bio3_project_communities where project_id = %s;", [projects[i]['id']])
                communities = dictfetchall(cursor)
                projects[i]['communities'] = []
                for j in range(0, len(communities)):
                    projects[i]['communities'].append(communities[j]['community_id'])
                
                cursor.execute("select profile_id from bio3_project_researchers where project_id = %s;", [projects[i]['id']])
                researchers = dictfetchall(cursor)
                projects[i]['researchers'] = []
                for j in range(0, len(researchers)):
                    projects[i]['researchers'].append(researchers[j]['profile_id'])

                cursor.execute("select concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, projects[i]['id']])
                projects[i]['images'] = dictfetchall(cursor)
                if len(projects[i]['images']) == 0:
                    projects[i]['images'] = [{'url': settings.MEDIA_URL+'projects/no_image_available.jpeg'}]

        return JsonResponse(projects, safe=False)

class ProjectExpandedDetail(APIView):

    def get_object(self, pk):
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):

        obj = self.get_object(pk)

        with connection.cursor() as cursor:
            cursor.execute("select project.id, project.name, project.description, project.created_at, uni.name as universidad, ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_AsText(ST_Transform(uni.location, 4326)) as uni_location, user2.id as user_id, user2.name as user_name, user2.last_name as user_last_name from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_customuser user2 on project.created_by_id = user2.id where project.is_active = true and project.id = %s;", [obj.id])
            projects = dictfetchall(cursor)
            for i in range(0, len(projects)):
                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(uni_assoc.location) as long_assoc, ST_Y(uni_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni_assoc on pu.university_id = uni_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['universities_network'] = dictfetchall(cursor)

                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(community_assoc.location) as long_assoc, ST_Y(community_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_communities pc on project.id = pc.project_id inner join bio3_community community_assoc on pc.community_id = community_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['communities_network'] = dictfetchall(cursor)

                cursor.execute("select uni.id, min(uni.name) as name, min(uni.long) as long, min(uni.lat) as lat, 10+exp(sum(uni.points)*0.001) as points from (select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*1 as points from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id where project.is_active = true and project.id = %s group by uni.id union all select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*0.5 as points from bio3_project project inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni on pu.university_id = uni.id where project.is_active = true and project.id = %s group by university_id) as uni group by uni.id;", [projects[i]['id'], projects[i]['id']])
                projects[i]['nodes_universities'] = dictfetchall(cursor)

                cursor.execute("select pc.community_id as id, min(community.name) as name, min(ST_X(community.location)) as long, min(ST_Y(community.location)) as lat, 10+exp((count(pc.community_id) * 0.5)*0.001) as points from bio3_project_communities pc inner join bio3_project project on pc.project_id = project.id inner join bio3_community community on pc.community_id = community.id where project.is_active = true and project.id = %s group by pc.community_id;", [projects[i]['id']])
                projects[i]['nodes_communities'] = dictfetchall(cursor)

                cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, projects[i]['id']])
                projects[i]['images'] = dictfetchall(cursor)

        return JsonResponse(projects[0], safe=False)

class ProjectNetworkExpandedList(APIView):
    
    def get(self, request, format=None):
        search = request.GET.get('search', None)

        if(search):
            search = '%' + search + '%'
            with connection.cursor() as cursor:
                cursor.execute("select distinct uni.id, uni.name, ST_X(uni.location) as long, ST_Y(uni.location) as lat, uni.created_at, usuario.id as id_user, usuario.name as user_name, usuario.last_name as user_last_name from bio3_university uni inner join bio3_project project on uni.id = project.main_university_id inner join bio3_customuser usuario on uni.created_by_id = usuario.id where project.is_active = true and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s);", [search, search])
                universities = dictfetchall(cursor)

                for i in range(0, len(universities)):
                    cursor.execute("select distinct projects.* from (select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.is_active = true and project.main_university_id = %s and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s) union all select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.is_active = true and project.main_university_id = %s and (unaccent(project.name) ilike %s or unaccent(project.description) ilike %s)) projects;", [universities[i]['id'], search, search, universities[i]['id'], search, search])
                    universities[i]['projects'] = dictfetchall(cursor)

                    for j in range(0, len(universities[i]['projects'])):
                        cursor.execute("select assoc.*, ROW_NUMBER() OVER(order by project_id asc, type desc, assoc_created_at asc) as rn from (select pu.project_id, uni.id as assoc_id, uni.name as assoc_name, ST_X(uni.location) as assoc_long, ST_Y(uni.location) as assoc_lat, uni.created_at as assoc_created_at, 'U' as type from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id where project.main_university_id = %s union all select pc.project_id, com.id as assoc_id, com.name as assoc_name, ST_X(com.location) as assoc_long, ST_Y(com.location) as assoc_lat, com.created_at as assoc_created_at, 'C' as type from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id where project.main_university_id = %s) assoc where assoc.project_id = %s;", [universities[i]['id'], universities[i]['id'], universities[i]['projects'][j]['id']])
                        universities[i]['projects'][j]['aristas'] = dictfetchall(cursor)
                    
                        cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, universities[i]['projects'][j]['id']])
                        universities[i]['projects'][j]['images'] = dictfetchall(cursor)
        else:
            with connection.cursor() as cursor:
                cursor.execute("select distinct uni.id, uni.name, ST_X(uni.location) as long, ST_Y(uni.location) as lat, uni.created_at, usuario.id as id_user, usuario.name as user_name, usuario.last_name as user_last_name from bio3_university uni inner join bio3_project project on uni.id = project.main_university_id inner join bio3_customuser usuario on uni.created_by_id = usuario.id where project.is_active = true;")
                universities = dictfetchall(cursor)

                for i in range(0, len(universities)):
                    cursor.execute("select distinct projects.* from (select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.is_active = true and project.main_university_id = %s union all select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.is_active = true and project.main_university_id = %s) projects;", [universities[i]['id'], universities[i]['id']])
                    universities[i]['projects'] = dictfetchall(cursor)

                    for j in range(0, len(universities[i]['projects'])):
                        cursor.execute("select assoc.*, ROW_NUMBER() OVER(order by project_id asc, type desc, assoc_created_at asc) as rn from (select pu.project_id, uni.id as assoc_id, uni.name as assoc_name, ST_X(uni.location) as assoc_long, ST_Y(uni.location) as assoc_lat, uni.created_at as assoc_created_at, 'U' as type from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id where project.main_university_id = %s union all select pc.project_id, com.id as assoc_id, com.name as assoc_name, ST_X(com.location) as assoc_long, ST_Y(com.location) as assoc_lat, com.created_at as assoc_created_at, 'C' as type from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id where project.main_university_id = %s) assoc where assoc.project_id = %s;", [universities[i]['id'], universities[i]['id'], universities[i]['projects'][j]['id']])
                        universities[i]['projects'][j]['aristas'] = dictfetchall(cursor)
                    
                        cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, universities[i]['projects'][j]['id']])
                        universities[i]['projects'][j]['images'] = dictfetchall(cursor)


        

        
        return JsonResponse(universities, safe=False)

class ProjectNetworkExpandedDetail(APIView):
    
    def get_object(self, pk):
        try:
            return Project.objects.get(id=pk, is_active=True)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        with connection.cursor() as cursor:
            cursor.execute("select distinct uni.id, uni.name, ST_X(uni.location) as long, ST_Y(uni.location) as lat, uni.created_at, usuario.id as id_user, usuario.name as user_name, usuario.last_name as user_last_name from bio3_university uni inner join bio3_project project on uni.id = project.main_university_id inner join bio3_customuser usuario on uni.created_by_id = usuario.id where project.id = %s and project.is_active = true;", [obj.id])
            universities = dictfetchall(cursor)

            for i in range(0, len(universities)):
                cursor.execute("select distinct projects.* from (select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.id = %s and project.main_university_id = %s union all select project.id, project.name, project.description, project.created_at, usuario.id as created_by, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where project.id = %s and project.main_university_id = %s) projects;", [obj.id, universities[i]['id'], obj.id, universities[i]['id']])
                universities[i]['projects'] = dictfetchall(cursor)

                for j in range(0, len(universities[i]['projects'])):
                    cursor.execute("select assoc.*, ROW_NUMBER() OVER(order by project_id asc, type desc, assoc_created_at asc) as rn from (select pu.project_id, uni.id as assoc_id, uni.name as assoc_name, ST_X(uni.location) as assoc_long, ST_Y(uni.location) as assoc_lat, uni.created_at as assoc_created_at, 'U' as type from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id where project.main_university_id = %s union all select pc.project_id, com.id as assoc_id, com.name as assoc_name, ST_X(com.location) as assoc_long, ST_Y(com.location) as assoc_lat, com.created_at as assoc_created_at, 'C' as type from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id where project.main_university_id = %s) assoc where assoc.project_id = %s;", [universities[i]['id'], universities[i]['id'], universities[i]['projects'][j]['id']])
                    universities[i]['projects'][j]['aristas'] = dictfetchall(cursor)
                    
                    cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, universities[i]['projects'][j]['id']])
                    universities[i]['projects'][j]['images'] = dictfetchall(cursor)

        return JsonResponse(universities, safe=False)


class ProfileDetail(APIView):
    
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(id=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)

        with connection.cursor() as cursor:
            cursor.execute("select usuario.id, usuario.email, usuario.name, usuario.last_name, usuario.date_joined, profile.description, profile.websites, degree.name as degree, fieldsofstudy.name as fieldofstudy, uni.id as university_id, uni.name as university from bio3_customuser usuario inner join bio3_profile profile on usuario.id = profile.user_id inner join bio3_degree degree on profile.degree_id = degree.id inner join bio3_fieldsofstudy fieldsofstudy on profile.field_of_study_id = fieldsofstudy.id inner join bio3_university uni on profile.university_id = uni.id where usuario.is_active = true and usuario.id = %s;;", [obj.id]) 
            user = dictfetchall(cursor)[0]

            cursor.execute("select distinct projects.* from (select project.id, project.name, project.description, project.created_by_id as created_by,  project.created_at, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_universities pu inner join bio3_university uni on pu.university_id = uni.id inner join bio3_project project on pu.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where usuario.id = %s union all select project.id, project.name, project.description, project.created_by_id as created_by, project.created_at, usuario.name as user_name, usuario.last_name as user_last_name from bio3_project_communities pc inner join bio3_community com on pc.community_id = com.id inner join bio3_project project on pc.project_id = project.id inner join bio3_customuser usuario on project.created_by_id = usuario.id where usuario.id = %s) projects order by projects.created_at desc;", [obj.id, obj.id])
            user['projects'] = dictfetchall(cursor)
        
        return JsonResponse(user, safe=False)
        

