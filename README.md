# DataInsight-AI

AI that allows users to perform AI analysis of uploaded datasets using prompts

# Instructions to run

- Install the requirements on either your local or virtual python environment by using `pip install -r .\requirements.txt`

# Considerations when creating this application

- Choice of backend framework: Flask VS FastAPI
  - FastAPI might be the better choice because of its performance advantages and modern features like async support, which can handle concurrent requests more efficiently
  - However, Flask is simple and easier to get starting with, and also has extensive documentation
  - I decided to use Flask research seems to suggest it is more beginner friendly (since this is my first python application). There is also not a very big need for efficiency since it is a simple app with only a few functions. However, in larger applications where asynchronous support may have a bigger impact, FastAPI might be better.
