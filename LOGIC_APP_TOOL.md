# Logic App Tool Details

## Tool name

```text
travelitinerarymailer_Tool
```

## Describe how to invoke the tool

```text
Use the travel itinerary mailer logic app tool to send a travel itinerary to a recipient.
Requires:
- Recipient email address (e.g. user@example.com)
- Subject - fill this is based on the content of the itinerary, e.g. "5-day Europe Trip"
- Body - Itinerary details - ensure this is only using HTML formatting not markdown so email clients can display it properly (e.g. <h1>, <b>, <ul>, <li>, <i>, etc.)
```

## Schema

```json
{
  "openapi": "3.0.3",
  "info": {
    "version": "1.0.0.0",
    "title": "travel-itinerary-mailer",
    "description": "Sends an travel itinerary to a recipient."
  },
  "servers": [
    {
      "url": "https://prod-05.australiaeast.logic.azure.com/workflows/a4d82cba59ef4336ad8178aefe9dff5a/triggers/When_an_HTTP_request_is_received/paths"
    }
  ],
  "security": [
    {
      "sig": []
    }
  ],
  "paths": {
    "/invoke": {
      "post": {
        "description": "Sends a travel itinerary to a recipient.",
        "operationId": "When_an_HTTP_request_is_received-invoke",
        "parameters": [
          {
            "name": "api-version",
            "in": "query",
            "description": "`2016-10-01` is the most common generally available version",
            "required": true,
            "schema": {
              "type": "string",
              "default": "2016-10-01"
            },
            "example": "2016-10-01"
          },
          {
            "name": "sv",
            "in": "query",
            "description": "The version number",
            "required": true,
            "schema": {
              "type": "string",
              "default": "1.0"
            },
            "example": "1.0"
          },
          {
            "name": "sp",
            "in": "query",
            "description": "The permissions",
            "required": true,
            "schema": {
              "type": "string",
              "default": "%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun"
            },
            "example": "%2Ftriggers%2FWhen_an_HTTP_request_is_received%2Frun"
          }
        ],
        "responses": {
          "200": {
            "description": "The travel itinerary mailer workflow response.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object"
                }
              }
            }
          },
          "default": {
            "description": "The Logic App Response.",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object"
                }
              }
            }
          }
        },
        "deprecated": false,
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "recipient": {
                    "type": "string"
                  },
                  "subject": {
                    "type": "string"
                  },
                  "body": {
                    "type": "string"
                  }
                }
              }
            }
          },
          "required": true
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "sig": {
        "type": "apiKey",
        "description": "The SHA 256 hash of the entire request URI with an internal key.",
        "name": "sig",
        "in": "query"
      }
    }
  }
}
```
