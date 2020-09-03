from distutils.core import setup

setup(
    name='pyAlfawise',
    packages=['pyAlfawise'],  # this must be the same as the name above
    install_requires=['voluptuous', 'netaddr'],
    version='0.7-beta',
    description='a simple python3 library for the Alfawise Humidifier',
    author='Hydreliox',
    author_email='hydreliox@gmail.com',
    url='https://github.com/HydrelioxGitHub/pyAlfawise',  # use the URL to the github repo
    download_url='https://github.com/HydrelioxGitHub/pyAlfawise/tarball/0.7-beta',
    keywords=['alfawise', 'humidifier', 'mist', 'API'],  # arbitrary keywords
    classifiers=[],
)
