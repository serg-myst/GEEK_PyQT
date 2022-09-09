from setuptools import setup, find_packages

setup(name="py_mess_client_svk",
      version="1.00",
      description="Mess Client",
      author="svk",
      author_email="svk@svk.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      )