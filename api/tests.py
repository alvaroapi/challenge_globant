from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Department, Job, HiredEmployee
import io

class UploadAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        # Create initial data needed for employee uploads if necessary
        Department.objects.create(id=1, department="Test Dept")
        Job.objects.create(id=1, job="Test Job")

    def test_upload_departments_csv_success(self):
        csv_content = "id,department\n2,New Dept 1\n3,New Dept 2"
        file = SimpleUploadedFile("departments.csv", csv_content.encode("utf-8"), content_type="text/csv")
        url = reverse("upload-departments")
        response = self.client.post(url, {"file": file}, format="multipart")
        
        # Check response status (should be 201 or 207 if using ignore_conflicts and existing data)
        self.assertIn(response.status_code, [201, 207]) 
        # Check if data exists in DB
        self.assertTrue(Department.objects.filter(id=2, department="New Dept 1").exists())
        self.assertTrue(Department.objects.filter(id=3, department="New Dept 2").exists())

    def test_upload_jobs_csv_success(self):
        csv_content = "id,job\n2,New Job 1\n3,New Job 2"
        file = SimpleUploadedFile("jobs.csv", csv_content.encode("utf-8"), content_type="text/csv")
        url = reverse("upload-jobs")
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertIn(response.status_code, [201, 207])
        self.assertTrue(Job.objects.filter(id=2, job="New Job 1").exists())
        self.assertTrue(Job.objects.filter(id=3, job="New Job 2").exists())

    def test_upload_employees_csv_success(self):
        # Ensure related objects exist
        if not Department.objects.filter(id=1).exists():
             Department.objects.create(id=1, department="Test Dept")
        if not Job.objects.filter(id=1).exists():
             Job.objects.create(id=1, job="Test Job")
             
        csv_content = "id,name,datetime,department_id,job_id\n101,Test Employee,2021-01-15T08:00:00Z,1,1\n102,Another Employee,2021-04-20T12:30:00Z,1,1"
        file = SimpleUploadedFile("employees.csv", csv_content.encode("utf-8"), content_type="text/csv")
        url = reverse("upload-employees")
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertIn(response.status_code, [201, 207])
        self.assertTrue(HiredEmployee.objects.filter(id=101, name="Test Employee").exists())
        self.assertTrue(HiredEmployee.objects.filter(id=102, name="Another Employee").exists())

    def test_upload_csv_invalid_format(self):
        file = SimpleUploadedFile("invalid.txt", b"invalid content", content_type="text/plain")
        url = reverse("upload-departments")
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("File must be a CSV", response.json()["error"])

    def test_upload_csv_missing_file(self):
        url = reverse("upload-departments")
        response = self.client.post(url, {}, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("No file provided", response.json()["error"])

    def test_upload_employees_csv_invalid_datetime(self):
        csv_content = "id,name,datetime,department_id,job_id\n103,Bad Date Employee,2021-13-01T08:00:00Z,1,1"
        file = SimpleUploadedFile("employees_bad_date.csv", csv_content.encode("utf-8"), content_type="text/csv")
        url = reverse("upload-employees")
        response = self.client.post(url, {"file": file}, format="multipart")
        self.assertEqual(response.status_code, 207) # Should complete with errors
        self.assertIn("errors", response.json())
        self.assertFalse(HiredEmployee.objects.filter(id=103).exists())

    def test_upload_employees_csv_invalid_fk(self):
        csv_content = "id,name,datetime,department_id,job_id\n104,Bad FK Employee,2021-02-01T08:00:00Z,99,99" # Assuming IDs 99 don't exist
        file = SimpleUploadedFile("employees_bad_fk.csv", csv_content.encode("utf-8"), content_type="text/csv")
        url = reverse("upload-employees")
        response = self.client.post(url, {"file": file}, format="multipart")
        # Depending on implementation (check before batch vs. DB constraint), status might vary
        # If check is done in view: 207 with errors
        # If relying on DB constraint and ignore_conflicts: 201/207 but record not inserted
        self.assertIn(response.status_code, [201, 207]) 
        if response.status_code == 207:
            self.assertIn("errors", response.json())
        self.assertFalse(HiredEmployee.objects.filter(id=104).exists())

class QueryAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create departments
        dept1 = Department.objects.create(id=1, department="Sales")
        dept2 = Department.objects.create(id=2, department="IT")
        dept3 = Department.objects.create(id=3, department="HR")
        # Create jobs
        job1 = Job.objects.create(id=1, job="Manager")
        job2 = Job.objects.create(id=2, job="Analyst")
        # Create employees hired in 2021
        HiredEmployee.objects.create(id=1, name="Emp 1", datetime="2021-01-10T10:00:00Z", department=dept1, job=job1) # Q1
        HiredEmployee.objects.create(id=2, name="Emp 2", datetime="2021-02-15T11:00:00Z", department=dept1, job=job1) # Q1
        HiredEmployee.objects.create(id=3, name="Emp 3", datetime="2021-04-05T12:00:00Z", department=dept1, job=job2) # Q2
        HiredEmployee.objects.create(id=4, name="Emp 4", datetime="2021-07-20T13:00:00Z", department=dept2, job=job1) # Q3
        HiredEmployee.objects.create(id=5, name="Emp 5", datetime="2021-08-10T14:00:00Z", department=dept2, job=job1) # Q3
        HiredEmployee.objects.create(id=6, name="Emp 6", datetime="2021-10-25T15:00:00Z", department=dept2, job=job2) # Q4
        HiredEmployee.objects.create(id=7, name="Emp 7", datetime="2021-11-11T16:00:00Z", department=dept2, job=job2) # Q4
        HiredEmployee.objects.create(id=8, name="Emp 8", datetime="2021-12-01T17:00:00Z", department=dept2, job=job2) # Q4
        # Create employees hired outside 2021
        HiredEmployee.objects.create(id=9, name="Emp 9", datetime="2020-12-31T23:59:59Z", department=dept1, job=job1)
        HiredEmployee.objects.create(id=10, name="Emp 10", datetime="2022-01-01T00:00:00Z", department=dept2, job=job2)
        # Create more hires in dept3 for avg test
        HiredEmployee.objects.create(id=11, name="Emp 11", datetime="2021-03-01T09:00:00Z", department=dept3, job=job1) # Q1
        HiredEmployee.objects.create(id=12, name="Emp 12", datetime="2021-03-02T09:00:00Z", department=dept3, job=job1) # Q1
        HiredEmployee.objects.create(id=13, name="Emp 13", datetime="2021-03-03T09:00:00Z", department=dept3, job=job1) # Q1
        HiredEmployee.objects.create(id=14, name="Emp 14", datetime="2021-03-04T09:00:00Z", department=dept3, job=job1) # Q1

    def test_hires_by_quarter_query(self):
        url = reverse("query-hires-by-quarter")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Expected: IT(5), Sales(3), HR(4) hires in 2021
        # Sales, Manager: Q1=2, Q2=0, Q3=0, Q4=0
        # Sales, Analyst: Q1=0, Q2=1, Q3=0, Q4=0
        # IT, Manager:    Q1=0, Q2=0, Q3=2, Q4=0
        # IT, Analyst:    Q1=0, Q2=0, Q3=0, Q4=3
        # HR, Manager:    Q1=4, Q2=0, Q3=0, Q4=0
        
        expected_results = [
            {"department": "HR", "job": "Manager", "Q1": 4, "Q2": 0, "Q3": 0, "Q4": 0},
            {"department": "IT", "job": "Analyst", "Q1": 0, "Q2": 0, "Q3": 0, "Q4": 3},
            {"department": "IT", "job": "Manager", "Q1": 0, "Q2": 0, "Q3": 2, "Q4": 0},
            {"department": "Sales", "job": "Analyst", "Q1": 0, "Q2": 1, "Q3": 0, "Q4": 0},
            {"department": "Sales", "job": "Manager", "Q1": 2, "Q2": 0, "Q3": 0, "Q4": 0},
        ]
        
        # Convert list of dicts to set of tuples for easier comparison (order doesn't matter)
        response_set = set(tuple(sorted(d.items())) for d in data)
        expected_set = set(tuple(sorted(d.items())) for d in expected_results)
        
        self.assertEqual(response_set, expected_set)

    def test_departments_above_average_query(self):
        url = reverse("query-departments-above-average")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Hires in 2021: Sales=3, IT=5, HR=4. Total = 12. Average = 12 / 3 = 4.0
        # Departments above average (> 4.0): IT (5 hires)
        # Expected output: [{'id': 2, 'department': 'IT', 'hired': 5}]
        
        expected_results = [
            {"id": 2, "department": "IT", "hired": 5},
            # HR has 4 hires, which is equal to the average, so it should not be included.
        ]
        
        # Convert list of dicts to set of tuples for easier comparison (order doesn't matter)
        response_set = set(tuple(sorted(d.items())) for d in data)
        expected_set = set(tuple(sorted(d.items())) for d in expected_results)
        
        self.assertEqual(response_set, expected_set)


