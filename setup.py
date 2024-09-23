from setuptools import setup

setup(
   name='whatsapp_survey_sender',
   version='1.0',
   description='Send surveis to chats in whatsapp. Made with python and selenium',
   author='Ismael Ortega',
   author_email='ismael.ortega.works@gmail.com',
   packages=['whatsapp_survey_sender'],  #same as name
   install_requires=[
      'selenium',
      'jsonata-python'
   ], #external packages as dependencies
)
