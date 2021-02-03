from rest_framework import serializers
from .models import CustomUser, Profile, University, Degree, FieldsOfStudy, Project, Community, ProjectImage



class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'

        extra_kwargs = {'users': {'required': False, 'allow_null': True}, 'universities': {'required': False, 'allow_null': True}, 'communities': {'required': False, 'allow_null': True}, 'researchers': {'required': False, 'allow_null': True}}
    
    def create(self, validated_data):
        obj = super(ProjectSerializer, self).create(validated_data)
        obj.save()
        return obj

class CustomUserSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'projects': {'required': False}}
        
    def create(self, validated_data):
        user = super(CustomUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {'projects': {'required': False, 'allow_null': True}}
        
    def create(self, validated_data):
        obj = super(ProfileSerializer, self).create(validated_data)
        obj.save()
        return obj

class UniversitySerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = '__all__'
        extra_kwargs = {'projects': {'required': False, 'allow_null': True}}
        
    def create(self, validated_data):
        obj = super(UniversitySerializer, self).create(validated_data)
        obj.save()
        return obj

class DegreeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Degree
        fields = '__all__'

class FieldsOfStudySerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldsOfStudy
        fields = '__all__'


# class ProjectXUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ProjectXUser
#         fields = '__all__'

class CommunitySerializer(serializers.ModelSerializer):

    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Community
        fields = '__all__'
        extra_kwargs = {'projects': {'required': False, 'allow_null': True}}

    def create(self, validated_data):
        obj = super(CommunitySerializer, self).create(validated_data)
        obj.save()
        return obj

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = '__all__'

# class ProjectXUniversitySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ProjectXUniversity
#         fields = '__all__'

# class ProjectXCommunitySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ProjectXCommunity
#         fields = '__all__'