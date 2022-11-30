# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mq_methods', 'mq_methods.client', 'mq_methods.worker']

package_data = \
{'': ['*']}

install_requires = \
['aiormq>=6.4.2,<7.0.0', 'nest-asyncio>=1.5.6,<2.0.0']

setup_kwargs = {
    'name': 'mq-methods',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'bilenko-ol',
    'author_email': 'bilenko.le@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
