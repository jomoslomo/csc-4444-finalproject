from setuptools import setup

setup(
    name='hand_tracking_app',
    version='1.0',
    install_requires=[
        'opencv-python',
        'mediapipe',
        'websocket-client',
    ],
)