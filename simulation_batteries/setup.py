from setuptools import setup, find_packages

setup(
    name="simulation_batteries",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "pandas>=1.3.0",
        "plotly>=5.1.0",
        "pytest>=6.2.0",
        "pydantic>=1.8.0",
        "PyYAML>=5.4.0",
        "networkx>=2.6.0",
        "loguru>=0.5.0",
        "typing-extensions>=3.10.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A sophisticated 3D sensor network simulation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sensor-network-simulation",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
