from setuptools import setup

setup(
    name="prison-break",
    description="Free yourself from the chains of having to"
    "acknowledging AGBs every time you connect to a captive portal",
    version="1.0.1",
    packages=["prisonbreak", "prisonbreak.plugins"],
    license="MIT",
    long_description=open("README.md").read(),
    author="Felix Richter",
    author_email="github@krebsco.de",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "docopt",
        "straight.plugin"
    ],
    entry_points={"console_scripts": ["prison-break = prisonbreak.cli:main"]},
    classifiers=[
        "Intended Audience :: Human",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
