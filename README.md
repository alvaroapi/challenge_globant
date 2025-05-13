# Globant Data Engineering Coding Challenge

Este proyecto implementa una API REST utilizando Django y Django REST Framework para cumplir con los requisitos del desafío de codificación de ingeniería de datos de Globant.

## Descripción General

La API permite:
1.  Cargar datos históricos desde archivos CSV para las tablas `departments`, `jobs` y `hired_employees` en una base de datos PostgreSQL.
2.  Realizar inserciones en batch (hasta 1000 filas por solicitud) para la carga de datos.
3.  Consultar métricas específicas a través de endpoints dedicados:
    *   Número de empleados contratados por trabajo y departamento en 2021, dividido por trimestre.
    *   Departamentos que contrataron más empleados que la media en 2021.

El proyecto también incluye:
*   Contenerización utilizando Docker y Docker Compose para facilitar el despliegue y la ejecución.

## Configuración y Ejecución (Usando Docker Compose)

**Requisitos previos:**
*   Docker
*   Docker Compose

**Pasos:**

1.  **Clonar el repositorio (o descomprimir el archivo .zip):**
    ```bash
    # git clone <repository_url>
    cd globant_challenge
    ```

2.  **Construir y ejecutar los contenedores:**
    ```bash
    docker-compose up --build -d
    ```
    Esto iniciará dos contenedores: `db` (PostgreSQL) y `web` (la aplicación Django).
    La aplicación Django aplicará automáticamente las migraciones de la base de datos al iniciar.

3. **Endpoints de la API**

La base de la URL es `http://localhost:8000/api/`.

**Carga de Datos (POST):**

*   `/upload/departments/`: Carga datos desde un archivo CSV a la tabla `departments`. Requiere un archivo llamado `file` en la solicitud multipart/form-data.
*   `/upload/jobs/`: Carga datos desde un archivo CSV a la tabla `jobs`. Requiere un archivo llamado `file`.
*   `/upload/employees/`: Carga datos desde un archivo CSV a la tabla `hired_employees`. Requiere un archivo llamado `file`.

**Consultas (GET):**

*   `/query/hires_by_quarter/`: Devuelve el número de empleados contratados por trabajo y departamento en 2021, dividido por trimestre.
*   `/query/departments_above_average/`: Devuelve la lista de departamentos que contrataron más empleados que la media en 2021.


## Consideraciones Adicionales

*   **Variables de Entorno:** La configuración de la base de datos en `docker-compose.yml` utiliza variables de entorno. Para producción, considera métodos más seguros para gestionar secretos.

*   **Escalabilidad:** La implementación utiliza `bulk_create` para la carga de datos, lo cual es más eficiente que inserciones individuales. Para cargas masivas muy grandes, se podrían explorar herramientas como `COPY` de PostgreSQL o procesamientos asíncronos con Celery.

