# StackSync - Secure Code Execution Service

A secure, containerized Python code execution service that allows running user-submitted Python code in a sandboxed environment. The service is built using Flask and nsjail for security, and supports popular data science libraries like pandas and numpy.

## Features

- 🔒 Secure code execution using nsjail sandboxing
- 📊 Support for data science libraries (pandas, numpy)
- 🚀 Containerized deployment (Docker)
- ☁️ Cloud Run compatible
- ⚡ Fast execution with resource limits
- 🔍 Detailed error reporting
- 📝 stdout/stderr capture

## Prerequisites

- Docker
- Python 3.10+
- Google Cloud Platform account (for Cloud Run deployment)

## Local Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd StackSync
```

2. Build the Docker image:

```bash
docker build -t flask-nsjail-api .
```

3. Run the container:

```bash
docker run --privileged -p 8080:8080 flask-nsjail-api
```

## API Usage

### Execute Code

**Endpoint:** `POST /execute`

**Request Body:**

```json
{
  "script": "def main():\n    import pandas as pd\n    print(\"Hello\")\n    return {\"message\": \"success\"}"
}
```

**Response:**

```json
{
  "result": {
    "message": "success"
  },
  "stdout": "Hello\n"
}
```

### Requirements

- The script must define a `main()` function
- The `main()` function must return a JSON-serializable value
- The script has a 5-second execution time limit
- Memory limit is set to 512MB

### Example Scripts

1. Basic DataFrame Operation:

```python
def main():
    import pandas as pd
    df = pd.DataFrame({"test": [1, 2, 3]})
    print("DataFrame created successfully")
    return {"status": "success", "data": df.to_dict()}
```

2. Statistical Analysis:

```python
def main():
    import pandas as pd
    import numpy as np
    data = {"A": np.random.rand(5), "B": np.random.rand(5)}
    df = pd.DataFrame(data)
    result = df.describe().to_dict()
    return {"status": "success", "statistics": result}
```

## Cloud Run Deployment

1. Build and tag the Docker image:

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/flask-nsjail-api .
```

2. Push to Google Container Registry:

```bash
docker push gcr.io/YOUR_PROJECT_ID/flask-nsjail-api
```

3. Deploy to Cloud Run:

```bash
gcloud run deploy flask-nsjail-api \
  --image gcr.io/YOUR_PROJECT_ID/flask-nsjail-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

## Security Features

- Code execution in isolated environment
- Resource limits (memory, CPU)
- Time limits
- Network access restrictions
- File system restrictions
- Process isolation

## Error Handling

The service provides detailed error messages for various scenarios:

- Missing main() function
- JSON serialization errors
- Execution timeouts
- Resource limit violations
- Python runtime errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [nsjail](https://github.com/google/nsjail) for sandboxing
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [pandas](https://pandas.pydata.org/) for data manipulation
- [numpy](https://numpy.org/) for numerical computations
