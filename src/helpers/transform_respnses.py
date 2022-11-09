def transform_user_response(user: dict) -> dict:
    """Transform user response to match the expected format."""
    user.pop('password')

    return user
