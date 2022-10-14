AD_SERVER_APP_ID = "xxxxxx-47cd-445d-a16e-xxxxxxxx"
API_AUDIENCE = f"api://{AD_SERVER_APP_ID}"
TENANT_ID = "xxxxxxxx-353f-4a85-be76-xxxxxxxxx"
JWT_URL = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
ISSUER = f"https://sts.windows.net/{TENANT_ID}/"
PATH_SCOPE = {
            "/vault": "GetSecret"
        }