from django.db import models

"""
due to the lack of information in the requirement, we are not using the ForeignKey relationships.
"""

class Department(models.Model):
    id = models.IntegerField(primary_key=True)
    department = models.CharField(max_length=255)

    def __str__(self):
        return self.department

class Job(models.Model):
    id = models.IntegerField(primary_key=True)
    job = models.CharField(max_length=255)

    def __str__(self):
        return self.job

class HiredEmployee(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    department_id = models.IntegerField(blank=True, null=True)
    job_id = models.IntegerField(blank=True, null=True)

    # department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, db_column="department_id")
    # job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True, db_column="job_id")

    def __str__(self):
        return self.name

