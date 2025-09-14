from django.shortcuts import render
from rest_framework import viewsets, permissions 
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework import status
from .serializers import * 
from .models import * 
from rest_framework.response import Response 
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from django.utils.dateparse import parse_datetime
import logging
from zoneinfo import ZoneInfo  # Using zoneinfo instead of pytz

logger = logging.getLogger(__name__)
User = get_user_model()

class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(): 
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user: 
                _, token = AuthToken.objects.create(user)
                return Response(
                    {
                        "user": self.serializer_class(user).data,
                        "token": token,
                        "userdetails":UserSerializer(user).data
                    }
                )
            else: 
                return Response({"error":"Invalid credentials"}, status=401)    
        else: 
            return Response(serializer.errors,status=400)



class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else: 
            print(serializer.errors)
            return Response(serializer.errors,status=400)


class UserViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self,request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        user=self.queryset.get(pk=pk)
        serializer=self.serializer_class(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
        
    def retrieve(self, request, pk=None):
        user=self.queryset.get(pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


    def update(self, request, pk=None):
        user=self.queryset.get(pk=pk)
        serializer=self.serializer_class(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)  
        
    def destroy(self, request, pk=None):
        user=self.queryset.get(pk=pk)
        user.delete()
        return Response(status=204)


class PatientViewset(viewsets.ViewSet): 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def list(self,request):
        queryset = Patient.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else: 
            print(serializer.errors)
            return Response(serializer.errors,status=400)

    def retrieve(self, request, pk=None):
        patient=self.queryset.get(pk=pk)
        serializer = self.serializer_class(patient)
        return Response(serializer.data)

    def update(self, request, pk=None):
        patient=self.queryset.get(pk=pk)
        serializer=self.serializer_class(patient,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)  

    def destroy(self, request, pk=None):
        patient=self.queryset.get(pk=pk)
        patient.delete()
        return Response(status=204)

class AppointmentsViewSet(viewsets.ModelViewSet):
    queryset = Appointments.objects.all()
    serializer_class = AppointmentsSerializer
  
    @action(detail=False, methods=['post'])
    def create_appointment(self, request):
        try:
            # Get the list of date-time strings from the form data
            date_times = request.data.getlist('dateTimes')
            patient = request.data.get('patient_id')
            reason = request.data.get('reason')
            doctor_assigned = request.data.get('doctor_assigned')
            patient_name = request.data.get('patient_name')
            appointment_status = request.data.get('appointment_status', 'Scheduled')

            if not date_times:
                return Response(
                    {"error": "No date times provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if 'appointment_status' not in request.data:
                request.data['appointment_status'] = 'Scheduled'

            # Define IST timezone
            ist_tz = ZoneInfo('Asia/Kolkata')
            
            # Create entries for each date-time
            entries = []
            for datetime_str in date_times:
                print(f"Received datetime string: {datetime_str}")
                
                # Parse the ISO format datetime string
                parsed_datetime = parse_datetime(datetime_str)
                
                if parsed_datetime:
                    # If the datetime is naive (no timezone), make it timezone-aware with IST
                    if timezone.is_naive(parsed_datetime):
                        # Set it to IST
                        parsed_datetime = parsed_datetime.replace(tzinfo=ist_tz)
                        print(f"Made naive datetime aware with IST: {parsed_datetime}")
                    
                    # If it has a timezone and it's not IST, convert to IST
                    elif parsed_datetime.tzinfo != ist_tz:
                        parsed_datetime = parsed_datetime.astimezone(ist_tz)
                        print(f"Converted to IST: {parsed_datetime}")
                    
                    # Store the datetime as IST without converting to UTC
                    # We'll create a naive datetime from the IST datetime
                    ist_datetime_naive = parsed_datetime.replace(tzinfo=None)
                    
                    # Create the database entry with the naive IST datetime
                    entry = Appointments(patient_id=patient, datetime=ist_datetime_naive, reason=reason, doctor_assigned=doctor_assigned, patient_name=patient_name, appointment_status=appointment_status)
                    entry.save()
                    entries.append(entry)
                    print(f"Saved datetime (IST): {ist_datetime_naive}")
            
            # Serialize the created entries for the response
            serializer = self.get_serializer(entries, many=True)
            
            return Response(
                {"message": f"Successfully saved {len(entries)} date times", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'])
    def get_appointments(self, request):
        try:
            # Get all appointments
            appointments = Appointments.objects.all()
            print(f"Total appointments fetched: {appointments}")
            # Process each appointment to treat it as IST
            ist_appointments = []
            for appointment in appointments:
                # Since we stored naive datetimes in IST, we'll just format them directly
                ist_appointments.append({
                    "id": appointment.id,
                    "patient_id": appointment.patient_id,
                    "datetime": appointment.datetime,
                    "reason": appointment.reason,
                    "doctor_assigned": appointment.doctor_assigned,
                    "created_at": appointment.created_at,
                    "patient_name": appointment.patient_name,
                    "appointment_status": appointment.appointment_status
                })
            print(f"Total IST appointments processed: {ist_appointments}")
            return Response(ist_appointments)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def destroy(self, request, pk=None):
        appointment = self.queryset.get(pk=pk)
        appointment.delete()
        return Response(status=204) 
    def update(self, request, pk=None):
        appointment=self.queryset.get(pk=pk)
        serializer=self.serializer_class(appointment,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)