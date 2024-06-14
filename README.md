# DataInsight-AI

AI that allows users to perform AI analysis of uploaded datasets using prompts
Prompts can include instructions for plotting charts (May not always work)

# Instructions to run

- Clone this repository and navigate here using a terminal
- Install the requirements on either your local or virtual python environment by using `pip install -r .\requirements.txt`
- In the .env file in this directory, insert the OpenAI API key

# Considerations when creating this application

- Choice of backend framework: Flask VS FastAPI:

  - FastAPI might be the better choice because of its performance advantages and modern features like async support, which can handle concurrent requests more efficiently
  - However, Flask is simple and easier to get starting with, and also has extensive documentation
  - I decided to use Flask research seems to suggest it is more beginner friendly (since this is my first python application). There is also not a very big need for efficiency since it is a simple app with only a few functions. However, in larger applications where asynchronous support may have a bigger impact, FastAPI might be better.

- Security of OpenAI API key:

  - The temporary OpenAI API key is not version controlled for security purposes (So others cannot obtain the key from github)

- ISSUE: Handling of prompts that request for plotting of images:

  - Pandas AI sometimes fail to recognise to not run "plt.show()", resulting in the AI rejecting the generated code as it would result in the code running until the Matplotlib GUI is closed. This results in the AI not being able to give an answer.
  - Upon testing, identical prompts may sometimes result in a success, and sometimes a failure. This is likely due to the internals of Pandas AI.
