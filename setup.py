from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='electrolens',
    version='0.0.1',
	author="Xiangyun (Ray) Lei",
    author_email="xlei38@gatech.edu",
    description="interactive visualization tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ray38/ElectroLens-python",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    packages=['electrolens'],
    include_package_data=True,

    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'ase',
        'cefpython3'
    ]
)