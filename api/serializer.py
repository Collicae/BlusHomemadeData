# serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import SignUp

class SignUp_Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = SignUp
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def validate_email(self, value):
        if SignUp.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def create(self, validated_data):
        user = SignUp(**validated_data)
        user.set_password(validated_data['password'])  # Ensure password is hashed
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'), username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = user
        return attrs

    
