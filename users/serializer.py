from rest_framework import serializers
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('phone', 'address', 'age', 'country', 'avatar')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UpdateProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'profile')
        read_only_fields = ('id', 'username', 'email', 'role')


    def update(self, instance, validated_data):
        profile_data = validated_data.get('profile')

        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=instance)
            profile.phone = profile_data.get('phone', profile.phone)
            profile.address = profile_data.get('address', profile.address)
            profile.age = profile_data.get('age', profile.age)
            profile.country = profile_data.get('country', profile.country)
            profile.avatar = profile_data.get('avatar', profile.avatar)
            profile.save()

        return instance
