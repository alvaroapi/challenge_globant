from django.urls import path
from .views import (
    DepartmentUploadView, 
    JobUploadView, 
    HiredEmployeeUploadView,
    HiresByQuarterView,
    DepartmentsAboveAverageView
)

urlpatterns = [
    # Upload endpoints
    path("upload/departments/", DepartmentUploadView.as_view(), name="upload-departments"),
    path("upload/jobs/", JobUploadView.as_view(), name="upload-jobs"),
    path("upload/employees/", HiredEmployeeUploadView.as_view(), name="upload-employees"),
    
    # Query endpoints
    path("query/hires_by_quarter/", HiresByQuarterView.as_view(), name="query-hires-by-quarter"),
    path("query/departments_above_average/", DepartmentsAboveAverageView.as_view(), name="query-departments-above-average"),
]

