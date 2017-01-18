from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='mblevenshtein',
      version='0.1',
      description='Functions related to Levenshtein distance',
      long_description=readme(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
      ],
      url='http://github.com/mbollmann/levenshtein',
      author='Marcel Bollmann',
      author_email='marcel@bollmann.me',
      license='MIT',
      packages=['mblevenshtein'],
      install_requires=[
          'lxml>=3.3.3'
      ],
      tests_require=[
          'unittest',
          'hypothesis>=1.12.0'
      ],
      include_package_data=True,
      zip_safe=False)
