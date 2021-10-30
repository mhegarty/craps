import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="craps",
    version="1.0.4",
    description="A table game engine.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mhegarty/craps",
    author="Mike Hegarty",
    author_email="mike@petorca.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["craps"],
    include_package_data=True,
    install_requires=[]                     # Install other dependencies if any
    # packages=["craps"],
    # include_package_data=True,
    # install_requires=["feedparser", "html2text"],
    # entry_points={
    #     "console_scripts": [
    #         "realpython=reader.__main__:main",
    #     ]
    # },
)

# python setup.py sdist bdist_wheel
# twine upload --skip-existing dist/*
