import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fluent_bdd",
    version="0.1.0",
    author="Pablo Chacin",
    author_email="pablochacin@",
    description="A fluend api for bdd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pablochacin/fluend-bdd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
