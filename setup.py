from setuptools import setup, find_packages

setup(
    name='statisticalSamplerAPI',
    version='0.1.0',
    description='A web API for generating random samples',
    author='Markus Musch',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'numpy',
        'pytest',
        'pydantic',
        'scipy',
        'uvicorn'
    ],
    python_requires='>=3.7.6',
    entry_points={
        'console_scripts': [
            'statistical-sampler-API-start = statisticalSamplerAPI.main:main'
        ]
    }
)
