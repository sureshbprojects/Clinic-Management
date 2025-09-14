from rest_framework import serializers 
from .models import * 
from django.contrib.auth import get_user_model 
User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret


class RegisterSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ('id','email','password', 'username')
        extra_kwargs = { 'password': {'write_only':True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name','date_joined', 'role')
        read_only_fields = ('id',)  

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'name', 'address', 'phone_number', 'emergency_contact', 'medical_history')
        read_only_fields = ('id',)

class AppointmentsSerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f", input_formats=["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "iso-8601"])
    class Meta:
        model = Appointments
        fields = ('id', 'patient_id', 'datetime', 'created_at', 'reason', 'doctor_assigned', 'patient_name', 'appointment_status')
        read_only_fields = ('id',)  