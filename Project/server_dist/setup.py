from setuptools import setup, find_packages

setup(name="py_mess_server_svk",
      version="1.01",
      description="Mess Server",
      author="svk",
      author_email="svk@svk.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      scripts=['server/server_run'],
      )