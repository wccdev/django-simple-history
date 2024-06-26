import subprocess
import sys
from glob import glob
from pathlib import Path

import django
from django.conf import settings
from django.core.management import call_command

from runtests import get_default_settings


def log(*args, **kwargs):
    # Flush so that all printed messages appear in the correct order, not matter what
    # `file` argument is passed (e.g. `sys.stdout` (default) or `sys.stderr`)
    print(*args, **{"flush": True, **kwargs})


def log_err(*args, **kwargs):
    log(*args, **{"file": sys.stderr, **kwargs})


# For some reason, changes in the .po files are often not reflected in the .mo files
# when running 'compilemessages' - unless the .mo files are deleted first,
# in which case they seem to be consistently updated
def delete_mo_files():
    locale_dir = Path("simple_history/locale")
    log(
        f"Deleting the following files inside '{locale_dir}'"
        f" so that they can be regenerated by 'compilemessages':"
    )
    for file_path in glob("**/*.mo", root_dir=locale_dir, recursive=True):
        log(f"\t{file_path}")
        (locale_dir / file_path).unlink()


# Code based on
# https://github.com/stefanfoulis/django-phonenumber-field/blob/e653a0972b56d39f1f51fa1f5124b70c2a5549bc/check-translations
def main():
    # Delete the .mo files before regenerating them below
    delete_mo_files()

    log("Running 'compilemessages'...")
    call_command("compilemessages")

    log("\nRunning 'git status'...")
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        stdout=subprocess.PIPE,
    )
    assert result.stderr is None
    stdout = result.stdout.decode()
    if stdout:
        log_err(f"Unexpected changes found in the workspace:\n\n{stdout}")
        if ".mo" in stdout:
            log_err(
                "To properly update any '.mo' files,"
                " try deleting them before running 'compilemessages'."
            )
        sys.exit(1)
    else:
        # Print the human-readable status to the console
        subprocess.run(["git", "status"])


if __name__ == "__main__":
    if not settings.configured:
        settings.configure(**get_default_settings())
    django.setup()
    main()
