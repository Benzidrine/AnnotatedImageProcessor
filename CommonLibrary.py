# --------------------
# Useful functions absent in python that should have been included
# --------------------

def IntTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False