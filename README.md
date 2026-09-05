# URL SHORTNER

A service to shorten long urls to shorter ones, with click counter traking and analystics.

## Current Scope : 
- It receives a long form url from the user, and shortens it to a 6 digit unique code
- It uses python random utility <code>secrets.choice()</code> to generate the unique code from 62 characters
- It uses in-memory data storage.

## Steps to run the Utility : 

1. Create a virtual env, so your local python installations are not affected.
> python3 -m venv .venv

2. Activate the virtual env
> source .venv/bin/activate 

3. Install the dependencies from requirements.txt file
> pip3 install -r requirements.txt

4. Run the ASGI server, with desired port number 
> uvicorn app.main:app --reload --port 9000


## Visit the Swagger
Visit http://localhost:9000/docs for the swagger docs.