The REST API example will run on port 5000 of host 0.0.0.0 (all interfaces) and be secured by SSL (self-signed certificate).

    python example/rest/rest.py

To secure your API with a username and password (*highly recommended if exposing to the live internet*), set the PYCIRCULATE_USERNAME and PYCIRCULATE_PASSWORD environment variables.

    PYCIRCULATE_USERNAME="myusername" PYCIRCULATE_PASSWORD="password" python examples/rest/rest.py
