from setuptools import setup, find_packages

setup(name='extract-readme',
      version='0.1',
      description='Extracts README and generates HTML',
      url='https://github.com/bchao1/extract-readme',
      author='Brian Chao',
      author_email='bchao.work@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      python_requires=">=3.6",
      entry_points = {
        'console_scripts': ['extract-readme=extract_readme.main:main'],
    }
)