import json
import subprocess
import tomllib


def main():
    with open("pyproject.toml", "rb") as fp:
        toml_data = tomllib.load(fp)
        flake8_bugbear_requires = toml_data["project"]["requires-python"]

    # get pypi data for flake8 as json
    curl_output = subprocess.getoutput(
        "curl -L -s --header 'Accept: application/vnd.pypi.simple.latest+json'"
        " https://pypi.org/simple/flake8"
    )
    flake8_pypi_data = json.loads(curl_output)

    # find latest non-yanked flake8 file data
    latest_file_data = next(
        file for file in reversed(flake8_pypi_data["files"]) if not file["yanked"]
    )
    flake8_requires = latest_file_data["requires-python"]

    assert flake8_requires == flake8_bugbear_requires, (
        f"python version requirements don't match: ({flake8_requires=} !="
        f" {flake8_bugbear_requires=})"
    )


if __name__ == "__main__":
    main()
