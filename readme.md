# Simple File Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure, containerized file management service built with Python and Flask. It provides both a user-friendly web interface for manual file operations and a versioned RESTful API for programmatic access, making it ideal for integration with services like n8n or other automated workflows.

## Key Features

*   **Web UI:** A clean user interface for managing files.
    *   Login/Logout with username and password.
    *   View a list of all available files.
    *   Upload one or more files at a time.
    *   Download or delete any file.
*   **RESTful API (`/api/v1/`):** A versioned API for automation.
    *   Protected by a secret API key sent in the `X-API-Key` request header.
    *   Endpoints to `list`, `upload`, `download`, and `delete` files.
    *   Consistent JSON error responses for all API routes.
*   **Interactive Documentation:**
    *   Automatically generated, interactive API documentation powered by Swagger/Flasgger.
    *   Available at the `/apidocs/` endpoint for developers to learn and test the API.
*   **Containerized & Portable:**
    *   Fully containerized with Docker and Docker Compose for easy setup and deployment.
    *   Push the image to Docker Hub to easily share it with your team.

## Architectural Patterns

This project uses modern Flask patterns to ensure the codebase is clean, maintainable, and scalable.

*   **Application Factory (`create_app`)**: Instead of a global `app` object, the application instance is created and configured within a function. This improves testability and avoids circular dependencies.
*   **Blueprints**: The application is broken down into logical components. The `main` blueprint handles the user-facing web UI, while the `api` blueprint handles all machine-to-machine RESTful interactions.
*   **Centralized Configuration**: For simplicity in this version, all configuration is managed via a `.env` file loaded at startup. This allows for easy changes to secrets and settings without modifying the code. Future versions could extend this to use more advanced configuration management tools for different environments (e.g., development vs. production).

## Getting Started

### Prerequisites

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### Docker Image

* https://hub.docker.com/r/sven0042/simple-file-server 
* pull it: `docker pull sven0042/simple-file-server:latest`


### 1. Set Up the Environment

First, clone the repository. Then, create a `.env` file in the root of the project by copying the example below. This file is used to store all your secrets and configurations.

**File: `.env`**
```ini
# The local path to the folder where files will be stored.
# This can be a relative path (like below) or an absolute path.
DOCUMENTS_ROOT=./shared_files

# --- Flask App Secrets ---
# Generate with: python -c 'import secrets; print(secrets.token_hex())'
FLASK_SECRET_KEY=your_super_secret_random_key_here
APP_USERNAME=admin
APP_PASSWORD=supersecret

# --- API Key for Programmatic Access (e.g., n8n) ---
# Generate with: python -c 'import secrets; print(secrets.token_hex(32))'
FILE_SERVER_API_KEY=your_newly_generated_long_and_random_api_key
```

### 2. Run the Application

With the `.env` file configured, start the service using Docker Compose.

```bash
# This command will build the image and start the service.
docker-compose up --build
```

You can now access the services:
*   **Web UI:** [http://localhost:8000](http://localhost:8000)
*   **API Documentation:** [http://localhost:8000/apidocs/](http://localhost:8000/apidocs/)

## Configuration Explained

The `.env` file controls all the critical settings for the application.

| Variable                      | Description                                                                                                                              | Default   |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `DOCUMENTS_ROOT`              | The path on the **host machine** where your shared files are stored.                                                                     | `./shared_files` |
| `FLASK_SECRET_KEY`            | A long, random string used by Flask to securely sign session cookies. **Required**.                                                      | `None`    |
| `APP_USERNAME`                | The username for logging into the web interface.                                                                                         | `None`    |
| `APP_PASSWORD`                | The password for logging into the web interface.                                                                                         | `None`    |
| `FILE_SERVER_API_KEY`         | A long, random secret key for accessing the API. **Required for API use**.                                                               | `None`    |
| `ENABLE_FILE_UPLOADS`         | If "true", enables the file upload API endpoint (`/api/v1/upload`).                                                                      | `true`    |
| `ENABLE_FILE_DOWNLOADS`       | If "true", enables the authenticated file download API endpoint (`/api/v1/files/...`).                                                   | `true`    |
| `ENABLE_FILE_DELETION`        | If "true", enables the file deletion API endpoint (`/api/v1/delete/...`).                                                                | `true`    |
| `ENABLE_HTTP_URL_DOWNLOADS`   | If "true", allows **unauthenticated** downloads via a direct URL (e.g., `http://localhost:8000/myfile.pdf`). **Use with caution.**          | `true`    |
| `HEALTH_CHECK_MODE`           | Sets the detail level for the `/api/v1/health` endpoint. Can be `simple` or `debug`. **Never use `debug` in production.**                 | `simple`  |

### Security Note on Public Downloads & Docker

The `ENABLE_HTTP_URL_DOWNLOADS` feature makes files publicly accessible. If you want to restrict this access only to other services within your Docker network (e.g., an internal n8n instance), you can comment out the `ports` section in your `docker-compose.yml` file.

```yaml
# In docker-compose.yml
services:
  fileserver:
    # ...
    # ports:
    #  - "8000:5000"  # <-- Commenting this out prevents access from the host machine
```

## API Usage Example

To use the API, you must include your API key in the `X-API-Key` header.

### List all files
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/v1/files
```

### Upload a file
```bash
curl -X POST \
  -H "X-API-Key: your_api_key_here" \
  -F "files=@/path/to/your/local/file.pdf" \
  http://localhost:8000/api/v1/upload
```

### Download a file
```bash
curl -H "X-API-Key: your_api_key_here" \
  -o "downloaded_file.pdf" \
  http://localhost:8000/api/v1/files/file.pdf
```

## Using the Pre-built Docker Hub Image

This repository is available as a pre-built image on Docker Hub at `sven0042/simple-file-server`. This is the recommended way for your team to run the service without needing the source code.

1.  Create a project directory with a `shared_files` folder and a `.env` file (as described above).
2.  Create the following `docker-compose.yml` file, which pulls the image directly from Docker Hub.

    ```yaml
    version: '3.8'

    services:
      fileserver:
        image: sven0042/simple-file-server:latest
        container_name: my_fileserver
        ports:
          - "8000:5000"
        volumes:
          - ./shared_files:/data
        restart: unless-stopped
        env_file:
          - ./.env
    ```
3.  Run the service:
    ```bash
    docker-compose up -d
    ```
