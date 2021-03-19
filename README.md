# KLINIFY BACKEND README

## Running the backend:
### Pre-requisites: Docker, Docker Compose
(Dependencies and database will be handled by Docker & Docker Compose)

```
docker-compose up
```

# API Documentation
## Authentication

```http
POST /login
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `username` | `string` | **Required**. Default: admin |
| `password` | `string` | **Required**. Default: admin |

Response: A JWT token will be returned. It can only be used once and will expire in 24h.

## Endpoints (JWT Required)
JWT should be passed as Bearer Token under Authorization header.

### Create Customer

```http
PUT /cust
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | **Required**.|
| `dob` | `string` | **Required**. Format: DDMMYYYY |

Response

```javascript
{
  "status" : "Created",
  "id" : int
}
```

### Retrieve Customer

```http
GET /cust/<string:id>
```

Response

```javascript
{
  "id" : int,
  "name" : string,
  "dob" : string,
  "updated_at" : string
}
```

### Edit Customer

```http
POST /cust/<string:id>
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `name` | `string` | **Optional**.|
| `dob` | `string` | **Optional**. Format: DDMMYYYY |

Response

```javascript
{
  "status" : "Updated"
}
```

### Delete Customer

```http
DELETE /cust/<string:id>
```

Response

```javascript
{
  "status" : "Deleted"
}
```

### List Youngest Customers

```http
GET /custlist
```

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `n` | `int` | **Required**.|

Response

```javascript
{
    "result": [
        {
            "id": int,
            "name": string,
            "dob": string,
            "updated_at": string
        },
        ...
    ]
}
```