from setuptools import setup
import sys


if sys.version_info.major < 3:
    sys.exit('Python < 3 is unsupported (for now).')
    

#def readfile(filename):
#    with open(filename, 'r+') as f:
#        return f.read()


setup(
    name="untappdscr",
    version="1.0.0",
    description="An https://untappd.com scrapper.",
    #long_description=readfile('README.md'),
    author="George Chousos",
    author_email="gxousos@gmail.com",
    url="https://github.com/GiorgosXou/untappdscr",
    packages=['untappdscr'],
)

# pip3 install .
# python setup.py sdist
# twine upload dist/*