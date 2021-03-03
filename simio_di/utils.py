import warnings


def get_origin(type_hint):
    warnings.warn("Get origin is not supported in Python <= 3.7")

    try:
        return type_hint.__origin__
    except AttributeError:
        return None


def get_args(type_hint):
    warnings.warn("Get args is not supported in Python <= 3.7")

    return type_hint.__args__
