import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="elasticache_for_app_performance",
    version="1.0.1",

    description="Launch app with EC2, Redis, S3, Lambda to Test Redis Performance",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Mystique",

    package_dir={"": "app_stacks"},
    packages=setuptools.find_packages(where="app_stacks"),

    install_requires=[
        "aws-cdk.core==1.30.0",
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
