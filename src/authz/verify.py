from functools import wraps

import jwt
from flask import request, _request_ctx_stack
from jwt import PyJWKClient

from src.configs.error_codes import errors
from src.configs import adapp
from src.appinsight.logger import get_logger

logger = get_logger(__name__)

# Error handler
class AppError(Exception):
    # def __init__(self, error, status_code):
    def __init__(self, error):
        self.error = error.message
        self.status_code = error.status_code


def verify_path_scope(roles: dict):
    path = request.path
    scope = adapp.PATH_SCOPE[path]

    if scope in roles:
        return True
    return False


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        logger.exception("Authorization header in missing from requests")
        raise AppError(errors.authorization_header_missing)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        logger.exception("Authorization header does not starts with Bearer")
        raise AppError(errors.invalid_auth_header_format_bearer)
    elif len(parts) == 1:
        logger.exception("Authorization header missing token")
        raise AppError(errors.invalid_auth_header_format_token)
    elif len(parts) > 2:
        logger.exception("Authorization header is malformed")
        raise AppError(errors.invalid_auth_header_format)
    token = parts[1]
    return token


def protected(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            jwk_client = PyJWKClient(adapp.JWT_URL)
            unverified_header = jwt.get_unverified_header(token)

            # Set default Signing Key from Token
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            # Verify kid with unverified_header and get signing Key. Azure AD has multiple Keys.
            for key in jwk_client.get_signing_keys():
                if key.key_id == unverified_header["kid"]:
                    signing_key = jwk_client.get_signing_key(key.key_id)
                    break

        except Exception as error:
            logger.exception(f"Error verifying token: {str(error)}")
            if isinstance(error, AppError):
                raise error
            else:
                raise AppError(errors.invalid_auth_header)
        if signing_key:
            try:
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience=adapp.API_AUDIENCE,
                    issuer=adapp.ISSUER,
                    verify=True
                )
            except jwt.ExpiredSignatureError:
                logger.exception(f"Access token has expired.")
                raise AppError(errors.token_expired)
            except (jwt.InvalidIssuerError,
                    jwt.InvalidAudienceError,
                    jwt.InvalidIssuedAtError,
                    jwt.InvalidTokenError) as error:
                logger.exception(f"Access token has invalid claims: {str(error)}")
                errors.invalid_claims.message['debug'] = str(error)
                raise AppError(errors.invalid_claims)
            except Exception as error:
                logger.exception(f"Authorization header has issue: {str(error)}")
                if isinstance(error, AppError):
                    raise error
                else:
                    raise AppError(errors.invalid_auth_header)
            if 'roles' not in payload:
                logger.exception(f"Access token missing roles.")
                raise AppError(errors.missing_role)

            if not verify_path_scope(payload['roles']):
                logger.exception(f"Access token missing required roles to access {request.path}")
                errors.missing_path_role.message['debug'] = f"Missing required role for accessing path {request.path}"
                raise AppError(errors.missing_path_role)

            _request_ctx_stack.top.current_user = payload
            # print(_request_ctx_stack.top.current_user)
            return f(*args, **kwargs)
        raise AppError(errors.invalid_header)

    return decorated

