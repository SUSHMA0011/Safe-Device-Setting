from copy import deepcopy


ALLOWED_LANGUAGES = {"en", "hi", "kn"}


def apply_update(current, actor, request):

    # 1. Check permission
    if not isinstance(actor, dict):
        return 403, {"error": "FORBIDDEN"}

    if actor.get("role") != "editor":
        return 403, {"error": "FORBIDDEN"}

    if actor.get("siteId") != current.get("siteId"):
        return 403, {"error": "FORBIDDEN"}

    # 2. Validate request structure
    if not isinstance(request, dict):
        return 422, {"error": "INVALID_INPUT"}

    if set(request) != {
        "deviceId", "expectedVersion", "settings"
    }:
        return 422, {"error": "INVALID_INPUT"}

    version = request["expectedVersion"]
    settings = request["settings"]

    if type(version) is not int or version < 1:
        return 422, {"error": "INVALID_INPUT"}

    if not isinstance(settings, dict) or not settings:
        return 422, {"error": "INVALID_INPUT"}

    # 3. Validate setting names
    if not set(settings).issubset({"language", "volume"}):
        return 422, {"error": "INVALID_INPUT"}

    # Validate language
    if "language" in settings:
        language = settings["language"]

        if (not isinstance(language, str)
                or language not in ALLOWED_LANGUAGES):
            return 422, {"error": "INVALID_INPUT"}

    # Validate volume
    if "volume" in settings:
        volume = settings["volume"]

        if type(volume) is not int or not 0 <= volume <= 5:
            return 422, {"error": "INVALID_INPUT"}

    # 4. Check device identity
    if request["deviceId"] != current.get("deviceId"):
        return 404, {"error": "NOT_FOUND"}

    # 5. Check version to prevent stale updates
    if version != current.get("version"):
        return 409, {"error": "CONFLICT"}

    # 6. Apply partial update to a copy
    updated = deepcopy(current)
    updated["settings"].update(deepcopy(settings))
    updated["version"] += 1

    return 200, updated