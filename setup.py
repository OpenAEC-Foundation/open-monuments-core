from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="core",
    version="0.1.0",
    description="Open-Monuments Core — Monumentenregister Frappe-app",
    author="OpenAEC Foundation",
    author_email="info@openaec.org",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
