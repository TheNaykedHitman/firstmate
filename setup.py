from setuptools import find_packages, setup

setup(
    name='firstmate-windows-orchestrator',
    version='0.1.0',
    description='Windows-native orchestrator for firstmate using Python and Orca CLI',
    author='Firstmate Refactoring Team',
    packages=find_packages(),
    install_requires=['pathlib2', 'subprocess32'],
    entry_points={'console_scripts': ['firstmate-orchestrate=firstmate_orchestrator.main:main']},
    python_requires='>=3.6',
)
