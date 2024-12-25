from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import SignUp
from .serializer import SignUp_Serializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

# This view will grab already existing users 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request):
    made_users = SignUp.objects.all()
    serializedUser = SignUp_Serializer(made_users, many=True)
    return Response(serializedUser.data)


# This view will create users
@api_view(["POST"])
def create_user(request):
    gotData = SignUp_Serializer(data=request.data)
    if gotData.is_valid():
        user =  gotData.save()
        refresh = RefreshToken.for_user(user)

        user_data = SignUp_Serializer(user).data

        return Response({
            'user_id': user.pk,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        })
    
    
    return Response(gotData.errors, status=400)

"""When posting data in the Create view
{
"first_Name": "Caleb", 
"last_Name": "Collins", 
"address": "58374 Shellhorn dr",
 "phone": 4751839985, 
 "Username": "Dr.GiggleTouch", 
 "Password": "popcorn123"
 }

 Follow this template inside the text area 
"""

"""
{
    "password": 
        "jasonstrong123."
    ,
    "email": 
        "JsonBetter@gmail.com"
    ,
    "first_name": 
        "Jason."
    ,
    "last_name": 
        "Strong."
    
}
"""

#This view will allow you to update existing users
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def update_user(request, pk):
    try:
        user = SignUp.objects.get(pk = pk)
    except SignUp.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    if request.method == "GET":
        serializer = SignUp_Serializer(user)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = SignUp_Serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)

        response = Response({
            'user_id': request.user.id,
            # Optionally return some user data
        })
        
        # Set cookies for access and refresh tokens
        response.set_cookie(
            key='access',
            value=str(refresh.access_token),
            httponly=True,  # Recommended for security
            samesite='Lax',  # Adjust according to your needs
            secure=True  # Set to True if using HTTPS
        )
        
        response.set_cookie(
            key='refresh',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=True
        )
        
        return response
    
class NotificationPreferencesView(APIView):
    #permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data from request
            email_preference = request.data.get('email', False)
            text_preference = request.data.get('text', False)
            user_email = request.data.get('email_address')
            user_phone = request.data.get('phone_number')

            # Validate required fields
            if not user_email or not user_phone:
                raise ValidationError("Both email and phone number are required.")

            # Send email confirmation if the email preference is True
            if email_preference:
                self.send_email_confirmation(user_email)

            # Send text confirmation if the text preference is True
            if text_preference:
                self.send_text_confirmation(user_phone)

            return Response({'message': 'Information sent successfully, please give time for infromation to be reached to you'}, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log error for server side debugging
            print(f"Error: {e}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_email_confirmation(self, user_email):
        try:
            send_mail(
                'Order Confirmation',
                'Thank you for your order. This is confirmation that we have recieved your order and are preparing it.\n\nPlease Leave at least 3-4 days before your order is shipped ',
                'Collicae100@gmail.com',  # Replace with the email that parents want to use
                [user_email],
                fail_silently=False,
            )
            print(f"Sent email to {user_email}")

        except Exception as e:
            print(f"Error sending email: {e}")
            raise Exception("Failed to send email.")

    #Text work just need to pay for service which i dont want to do right now so wait for parents acceptance first
    def send_text_confirmation(self, user_phone):
        try:
            # Retrieve Twilio credentials from Django settings
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            twilio_phone_number = settings.TWILIO_PHONE_NUMBER

            # Initialize the Twilio client
            client = Client(account_sid, auth_token)

            # Send SMS message
            message = client.messages.create(
                body="Thank you for your order. You will be notified via text.",
                from_=twilio_phone_number,
                to=+13174904813,
            )
            print(f"Sent message to {user_phone}: {message.sid}")

        except Exception as e:
            print(f"Error sending text: {e}")
            raise Exception("Failed to send SMS.")