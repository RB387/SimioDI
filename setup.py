import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="simio_di",
    version="0.1.1",
    author="Nikita Zavadin",
    author_email="zavadin142@gmail.com",
    description="Small and simple Dependency Injector. Made for Simio framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="https://github.com/RB387/simio-di",
    packages=setuptools.find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.7",
)
