from rest_framework import serializers
from .models import Department, Job, HiredEmployee
from django.utils.dateparse import parse_datetime

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "department"]

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "job"]

class HiredEmployeeSerializer(serializers.ModelSerializer):
    # Use IntegerField for foreign keys during input validation
    department_id = serializers.IntegerField()
    job_id = serializers.IntegerField()
    datetime = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", input_formats=["%Y-%m-%dT%H:%M:%SZ"])

    class Meta:
        model = HiredEmployee
        fields = ["id", "name", "datetime", "department_id", "job_id"]

    def validate_datetime(self, value):
        # Ensure datetime is parsed correctly, although DRF handles it with input_formats
        if isinstance(value, str):
            parsed_dt = parse_datetime(value)
            if parsed_dt is None:
                raise serializers.ValidationError("Invalid datetime format. Use ISO format YYYY-MM-DDTHH:MM:SSZ.")
            return parsed_dt
        return value

    def create(self, validated_data):
        # Pop the _id fields and use the object fields for creation
        department_id = validated_data.pop("department_id")
        job_id = validated_data.pop("job_id")
        try:
            department = Department.objects.get(pk=department_id)
            job = Job.objects.get(pk=job_id)
            employee = HiredEmployee.objects.create(department=department, job=job, **validated_data)
            return employee
        except Department.DoesNotExist:
            raise serializers.ValidationError(f"Department with id {department_id} does not exist.")
        except Job.DoesNotExist:
            raise serializers.ValidationError(f"Job with id {job_id} does not exist.")

