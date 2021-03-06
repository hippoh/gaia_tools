from setuptools import setup #, Extension

long_description = "Tools for working with the @ESAGaia data and related data sets; see `here <https://github.com/jobovy/gaia_tools>`__ for further documentation"

setup(name='gaia_tools',
      version='0.1',
      description='Gaia data tools',
      author='Jo Bovy',
      author_email='bovy@astro.utoronto.ca',
      license='MIT',
      long_description=long_description,
      url='https://github.com/jobovy/gaia_tools',
      package_dir = {'gaia_tools/': ''},
      packages=['gaia_tools','gaia_tools/load',
                'gaia_tools/xmatch','gaia_tools/select'],
      package_data={'gaia_tools/select':['2massc_hp5.txt'],
                    "": ["README.rst","LICENSE"]},
      install_requires=['numpy','astropy','fitsio','tqdm','healpy']
      )
