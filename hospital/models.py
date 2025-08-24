from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import AbstractUser

# ✅ Extend Django's built-in user model for authentication
class User(AbstractUser):
    ROLES = (
        ('management', 'Management'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=20, choices=ROLES)

    def _str_(self):
        return f"{self.username} ({self.role})"


# ✅ Management (inherits from User via OneToOne)
class Management(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def create_doctor(self, name, specialization, email, password):
        doctor_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role='doctor'
        )
        doctor = Doctor.objects.create(user=doctor_user, specialization=specialization)
        return doctor

    def create_patient(self, name, email, password, age=None):
        patient_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role='patient'
        )
        patient = Patient.objects.create(user=patient_user, age=age)
        return patient

    def _str_(self):
        return f"Management: {self.user.username}"


# ✅ Doctor
class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)

    def _str_(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"


# ✅ Patient
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name="patients")
    dob = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)  # 🔹 Added Age Field
    gender = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def _str_(self):
        return f"Patient: {self.user.get_full_name()}"


# ✅ Vitals (Updated Fields)
class Vitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="vitals")

    # Anthropometrics
    bmi = models.FloatField()
    cholesterol = models.FloatField()
    blood_pressure = models.CharField(max_length=20)   # store as "120/80"

    # Comorbidities
    diabetes = models.CharField(max_length=5, choices=[("Yes", "Yes"), ("No", "No")])
    hypertension = models.CharField(max_length=5, choices=[("Yes", "Yes"), ("No", "No")])

    # Hospitalization details
    medication_count = models.IntegerField()
    length_of_stay = models.IntegerField()
    discharge_destination = models.CharField(
        max_length=50,
        choices=[
            ("Home", "Home"),
            ("Nursing_Facility", "Nursing Facility"),
            ("Other", "Other"),
        ]
    )

    # Auto fields
    date_recorded = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Vitals of {self.patient.user.username} on {self.date_recorded.strftime('%Y-%m-%d')}"


# ✅ Prediction Model (stores AI prediction results)
class Prediction(models.Model):
    vitals = models.ForeignKey(Vitals, on_delete=models.CASCADE, related_name="predictions")
    risk_score = models.FloatField()
    predicted_readmit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Prediction for {self.vitals.patient.user.username}: {self.risk_score}"


# ✅ Prediction Model (stores AI prediction results)
class Prediction(models.Model):
    vitals = models.ForeignKey(Vitals, on_delete=models.CASCADE, related_name="predictions")
    risk_score = models.FloatField()
    predicted_readmit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for {self.vitals.patient.user.username}: {self.risk_score}"
