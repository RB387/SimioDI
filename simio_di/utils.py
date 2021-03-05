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


def deep_merge_dicts(lhs: dict, rhs: dict) -> dict:
    for key, value in rhs.items():
        if isinstance(value, dict):
            node = lhs.setdefault(key, {})
            deep_merge_dicts(node, value)
        else:
            lhs[key] = value

    return lhs
