import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="fritzscraper",
    version="0.0.1",
    author="Clemens Boos",
    author_email="clemensboos@gmail.com",
    description="AVM FRITZ!Box status scraper and Prometheus exporter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-fritzscraper-exporter=fritzscraper.exporter:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'pandas',
        'prometheus_client',
        'requests'
    ],
    python_requires='>=3.7'
)
