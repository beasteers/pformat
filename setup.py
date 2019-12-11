import setuptools

setuptools.setup(name='pformat',
                 version='0.0.1',
                 description='Advanced python string formatting',
                 # long_description=open('README.md').read().strip(),
                 author='Bea Steers',
                 author_email='bea.steers@gmail.com',
                 # url='http://path-to-my-packagename',
                 packages=setuptools.find_packages(),
                 install_requires=[ 'parse' ],
                 license='MIT License',
                 keywords='string format partial glob regex default')
