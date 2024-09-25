from setuptools import setup, find_packages

setup(
    name='nanows',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'websockets'
    ],
    python_requires='>=3.6',
    description='A Python WebSocket API for interacting with Nano cryptocurrency nodes.',
    author='gr0vity',
    author_email='iq.cc@pm.me',
    url='https://github.com/gr0vity-dev/nanows',
    keywords='nano cryptocurrency websocket api',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
