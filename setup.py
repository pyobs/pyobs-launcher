from setuptools import setup

setup(
    name='pyobs-launcher',
    version='0.9',
    description='GUI launcher for pyobs',
    author='Tim-Oliver Husser',
    author_email='thusser@uni-goettingen.de',
    packages=['pyobs_launcher'],
    entry_points={
        'gui_scripts': [
            'pyobs-launcher=pyobs_launcher.__init__:main',
        ]
    },
    install_requires=['PyQt5', 'PyYAML']
)
