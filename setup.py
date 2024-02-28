from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open("requirements.txt", "r") as file:
    requirements = file.read().splitlines()

setup(
    name="mle_project_challenge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "pytest-xdist", "pylint", "pylint-quotes", "black", "mypy==1.1.1", "isort"]
    },
)
