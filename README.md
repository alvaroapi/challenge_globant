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
    # git clone https://github.com/alvaroapi/challenge_globant.git
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


## Ventajas de trabajar con archivos .pbir en lugar de .pbix

Los archivos `.pbir` (Power BI Report) son el formato de definición de informe basado en texto introducido por Microsoft como parte del proyecto **Power BI Enhanced Report Format**. A continuación se detallan las principales ventajas de utilizar `.pbir` frente al formato binario `.pbix`:

### 1. Compatible con control de versiones (Git)
Los archivos `.pbir` se almacenan como una estructura de carpetas con archivos de texto (JSON), lo que los hace perfectamente compatibles con sistemas de control de versiones como Git. Esto permite:
- Realizar **diffs** entre versiones para ver exactamente qué cambió en el informe.
- Gestionar **ramas y merges** de informes de forma colaborativa.
- Mantener un **historial completo de cambios** con mensajes de commit descriptivos.

### 2. Trabajo colaborativo
Al poder utilizar Git y plataformas como GitHub o Azure DevOps, múltiples desarrolladores pueden trabajar en el mismo informe simultáneamente, gestionar conflictos y revisar cambios mediante **pull requests** antes de integrarlos.

### 3. Modularidad y separación de capas
El formato `.pbir` separa el informe de su modelo semántico (dataset). El informe solo contiene la definición visual (páginas, visualizaciones, filtros), mientras que el modelo de datos puede mantenerse de forma independiente. Esto favorece la **reutilización del modelo** en múltiples informes.

### 4. Menor tamaño de archivo
Dado que `.pbir` no incorpora los datos en el propio archivo (a diferencia de `.pbix` cuando se utiliza importación de datos), el tamaño del archivo es considerablemente menor y más manejable.

### 5. Automatización y CI/CD
Al ser archivos de texto, es posible manipularlos mediante scripts y herramientas de automatización para:
- Modificar definiciones de informes de forma programática.
- Integrarlos en **pipelines de CI/CD** para publicación automática en el servicio de Power BI.
- Generar o transformar informes mediante código.

### 6. Mayor transparencia y auditabilidad
Los cambios en el informe (páginas eliminadas, medidas modificadas, filtros actualizados) quedan registrados de forma legible en el historial de commits, facilitando la **auditoría y trazabilidad** de los cambios.

### Resumen comparativo

| Característica                      | `.pbix`                    | `.pbir`                          |
|-------------------------------------|----------------------------|----------------------------------|
| Formato                             | Binario                    | Texto (JSON / carpetas)          |
| Compatible con Git                  | ❌ Limitado                 | ✅ Sí                            |
| Trabajo colaborativo                | ❌ Difícil                  | ✅ Sí, con pull requests         |
| Incluye datos                       | ✅ Sí (modo importación)    | ❌ No (referencia al dataset)    |
| Automatización / CI/CD              | ❌ Difícil                  | ✅ Sí                            |
| Auditabilidad de cambios            | ❌ No                       | ✅ Sí                            |
| Separación informe / modelo         | ❌ Todo en uno              | ✅ Sí                            |

> **Nota:** El formato `.pbir` requiere tener habilitada la opción **"Power BI Project (.pbip)"** en la configuración de Power BI Desktop (actualmente en versión preliminar).

---

## Consideraciones Adicionales

*   **Variables de Entorno:** La configuración de la base de datos en `docker-compose.yml` utiliza variables de entorno. Para producción, considera métodos más seguros para gestionar secretos.

*   **Escalabilidad:** La implementación utiliza `bulk_create` para la carga de datos, lo cual es más eficiente que inserciones individuales. Para cargas masivas muy grandes, se podrían explorar herramientas como `COPY` de PostgreSQL o procesamientos asíncronos con Celery.

