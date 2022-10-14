from box import Box


def auth_error():
    auth_error_codes = {
        "authorization_header_missing": {
            "message": {
                "code": "AuthorizationHeaderMissing",
                "description": "Authorization header is missing from the request"
            },
            "status_code": 401
        },
        "invalid_auth_header_format_bearer": {
            "message": {
                "code": "InvalidAuthorizationHeader",
                "description": "Authorization header must start with Bearer"
            },
            "status_code": 401
        },
        "invalid_auth_header_format_token": {
            "message": {
                "code": "AuthorizationTokenNotFound",
                "description": "Authorization does not contain Token"
            },
            "status_code": 401

        },
        "invalid_auth_header_format": {
            "message": {
                "code": "InvalidAuthorizationHeaderFormat",
                "description": "Authorization header must be Bearer token"
            },
            "status_code": 401

        },
        "invalid_auth_header": {
            "message": {
                "code": "InvalidAuthorizationHeader",
                "description": "Unable to parse authentication token"
            },
            "status_code": 401

        },
        "token_expired": {
            "message": {
                "code": "AuthorizationTokenExpired",
                "description": "Authorization bearer token is expired."
            },
            "status_code": 401

        },
        "invalid_claims": {
            "message": {
                "code": "InvalidAuthorizationClaims",
                "description": "Failed to validate authorization claims."
            },
            "status_code": 401

        },
        "invalid_header": {
            "message": {
                "code": "InvalidAuthorizationHeader",
                "description": "Unable to find appropriate key"
            },
            "status_code": 401

        },
    }

    return auth_error_codes


def bad_gateway():
    bad_gateway_codes = {
        "vault_error": {
            "message": {
                "code": "AzureKeyVaultFatalError",
                "description": "Error getting response from Azure Key Vault."
            },
            "status_code": 502

        }
    }

    return bad_gateway_codes


def not_found():
    not_found_codes = {
        "secret_not_found": {
            "message": {
                "code": "SecretNotFound",
                "description": "Requested secret not found in Key Vault."
            },
            "status_code": 404

        }
    }

    return not_found_codes


def function_errors():
    function_error_code = {
        "health_check_failed": {
            "message": {
                "code": "ServiceHealthCheckDown",
                "description": "Function App health Check failed.",
            },
            "status_code": 500
        },
        "unsupported_content_type": {
            "message": {
                "code": "InvalidContentType",
                "description": "Content-Type is not supported"
            },
            "status_code": 500

        }
    }

    return function_error_code


errors = Box({**auth_error(), **bad_gateway(), **not_found(), **function_errors()})