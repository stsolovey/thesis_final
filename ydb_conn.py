import posixpath
import ydb

def is_directory_exists(driver, path):
    try:
        return driver.scheme_client.describe_path(path).is_directory()
    except ydb.SchemeError:
        return False
def ensure_path_exists(driver, database, path):
    paths_to_create = list()
    path = path.rstrip("/")
    while path not in ("", database):
        full_path = posixpath.join(database, path)
        if is_directory_exists(driver, full_path):
            break
        paths_to_create.append(full_path)
        path = posixpath.dirname(path).rstrip("/")

    while len(paths_to_create) > 0:
        full_path = paths_to_create.pop(-1)
        driver.scheme_client.make_directory(full_path)