from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction, connection
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse # Import HttpResponse
import csv
import io

from .models import Department, Job, HiredEmployee
from .serializers import DepartmentSerializer, JobSerializer, HiredEmployeeSerializer

# --- Upload Views ---
class BaseUploadView(views.APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = None
    model_class = None
    batch_size = 1000
    form_title = "Upload CSV File"
    expected_header = [] # To be defined in child classes

    def get(self, request, *args, **kwargs):
        # HTML form to be displayed
        html_form = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>{self.form_title}</title>
        </head>
        <body>
            <h2>{self.form_title}</h2>
            <p>Nota: El archivo CSV no debe contener una fila de encabezado.</p>
            <form action="{ request.path }" method="post" enctype="multipart/form-data">
                <label for="file">Selecciona el archivo CSV (sin encabezado):</label>
                <input type="file" name="file" id="file" accept=".csv" required>
                <br><br>
                <input type="submit" value="Cargar Archivo">
            </form>
        </body>
        </html>
        """
        return HttpResponse(html_form, content_type="text/html")

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.endswith(".csv"):
            return Response({"error": "File must be a CSV."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not self.expected_header:
            return Response({"error": "Expected header not defined for this view."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            from django.core.management import call_command
            call_command("migrate") # Ensure migrations are applied

            decoded_file = file_obj.read().decode("utf-8")
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            # No longer reading header from file: header = next(reader)

            objects_to_create = []
            errors = []
            row_count = 0
            total_inserted = 0

            with transaction.atomic():
                for row_number, row in enumerate(reader, start=1): # Start from line 1 as there's no header
                    if not row: # Skip empty rows
                        continue
                    
                    # Check for column count consistency against expected_header
                    if len(row) != len(self.expected_header):
                        errors.append(f"Row {row_number}: Incorrect number of columns. Expected {len(self.expected_header)}, got {len(row)}.")
                        continue

                    data = dict(zip(self.expected_header, row))
                    
                    if self.model_class == HiredEmployee and "datetime" in data:
                        dt_str = data["datetime"]
                        parsed_dt = parse_datetime(dt_str)
                        if parsed_dt is None:
                             errors.append(f"Row {row_number}: Invalid datetime format '{dt_str}'. Use ISO format YYYY-MM-DDTHH:MM:SSZ.")
                             continue
                        data["datetime"] = parsed_dt
                        
                    serializer = self.serializer_class(data=data)
                    if serializer.is_valid():
                        validated_data = serializer.validated_data
                        instance_data = {}
                        for field, value in validated_data.items():
                            instance_data[field] = value
                        if self.model_class == HiredEmployee:
                            try:
                                department_id = instance_data.pop("department_id")
                                job_id = instance_data.pop("job_id")
                                instance_data["department_id"] = department_id
                                instance_data["job_id"] = job_id
                            except KeyError:
                                errors.append(f"Row {row_number}: Missing department_id or job_id in data {data}. Ensure CSV structure matches expected: {self.expected_header}")
                                continue
                        objects_to_create.append(self.model_class(**instance_data))
                        row_count += 1
                        if row_count >= self.batch_size:
                            try:
                                self.model_class.objects.bulk_create(objects_to_create, ignore_conflicts=True)
                                total_inserted += len(objects_to_create)
                            except Exception as bulk_e:
                                errors.append(f"Bulk create error: {str(bulk_e)}")
                            objects_to_create = []
                            row_count = 0
                    else:
                        errors.append(f"Row {row_number}: {serializer.errors}")
                if objects_to_create:
                    try:
                        self.model_class.objects.bulk_create(objects_to_create, ignore_conflicts=True)
                        total_inserted += len(objects_to_create)
                    except Exception as bulk_e:
                        errors.append(f"Bulk create error (final batch): {str(bulk_e)}")
            if errors:
                return Response({"message": f"Completed with errors. Inserted approximately {total_inserted} records.", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
            else:
                final_count = self.model_class.objects.count()
                return Response({"message": f"Successfully processed file. Total records in table: {final_count}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DepartmentUploadView(BaseUploadView):
    serializer_class = DepartmentSerializer
    model_class = Department
    form_title = "Cargar Archivo CSV de Departamentos (sin encabezado)"
    expected_header = ["id", "department"]

class JobUploadView(BaseUploadView):
    serializer_class = JobSerializer
    model_class = Job
    form_title = "Cargar Archivo CSV de Trabajos (sin encabezado)"
    expected_header = ["id", "job"]

class HiredEmployeeUploadView(BaseUploadView):
    serializer_class = HiredEmployeeSerializer
    model_class = HiredEmployee
    form_title = "Cargar Archivo CSV de Empleados Contratados (sin encabezado)"
    expected_header = ["id", "name", "datetime", "department_id", "job_id"]

# --- Query Views ---
class HiresByQuarterView(views.APIView):
    def get(self, request, *args, **kwargs):
        query = """
            SELECT 
            d.department,
            j.job,
            COUNT(*) FILTER (WHERE EXTRACT(quarter FROM h.datetime) = 1) AS Q1,
            COUNT(*) FILTER (WHERE EXTRACT(quarter FROM h.datetime) = 2) AS Q2,
            COUNT(*) FILTER (WHERE EXTRACT(quarter FROM h.datetime) = 3) AS Q3,
            COUNT(*) FILTER (WHERE EXTRACT(quarter FROM h.datetime) = 4) AS Q4
            FROM api_hiredemployee h
            INNER JOIN api_department d ON h.department_id = d.id
            INNER JOIN api_job j ON h.job_id = j.id
            WHERE EXTRACT(year FROM h.datetime) = 2021
            GROUP BY d.department, j.job
            ORDER BY d.department, j.job;
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DepartmentsAboveAverageView(views.APIView):
    def get(self, request, *args, **kwargs):
        query = """
        WITH DepartmentHires2021 AS (
            SELECT
                d.id,
                d.department,
                COUNT(he.id) AS hired_count
            FROM
                api_department d
            JOIN
                api_hiredemployee he ON d.id = he.department_id
            WHERE
                EXTRACT(YEAR FROM he.datetime) = 2021
            GROUP BY
                d.id,
                d.department
        ),
        AverageHires2021 AS (
            SELECT AVG(hired_count) AS avg_hires
            FROM DepartmentHires2021
        )
        SELECT
            dh.id,
            dh.department,
            dh.hired_count AS hired
        FROM
            DepartmentHires2021 dh,
            AverageHires2021 avg
        WHERE
            dh.hired_count > avg.avg_hires
        ORDER BY
            dh.hired_count DESC;
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
