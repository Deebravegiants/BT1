# [M] Path Normalization Bypass in Traefik Router + Middleware Rules

## Summary
Severity: Medium
Advisory: GHSA-gm3x-23wp-hc2c
CVE: CVE-2025-66490
CWE: CWE-436
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-gm3x-23wp-hc2c
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.32
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.3

## Details
## Impact

There is a potential vulnerability in Traefik managing the requests using a `PathPrefix`, `Path` or `PathRegex` matcher.

When Traefik is configured to route the requests to a backend using a matcher based on the path; if the request path contains an encoded restricted character from the following set **('/', '\', 'Null', ';', '?', '#')**, it’s possible to target a backend, exposed using another router, by-passing the middlewares chain.

## Example

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-service
spec:
  routes:
    - match: PathPrefix(‘/admin/’)
      kind: Rule
      services:
        - name: service-a
          port: 8080
      middlewares:
        - name: my-security-middleware
    - match: PathPrefix(‘/’)
      kind: Rule
      services:
        - name: service-a
          port: 8080
```

In such a case, the request `http://mydomain.example.com/admin%2F` will reach the backend `service-a` without operating the middleware `my-security-middleware` and passing the security put in place for the `/admin/` path.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.32
- https://github.com/traefik/traefik/releases/tag/v3.6.4

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>### Summary
A vulnerability exists in Traefik’s path matching logic that allows attackers to bypass access-control middleware (e.g., blocking rules) by using URL-encoded paths. I found this vulnerability while playing PwnSec CTF 2025 with my team @0xL4ugh

### Details
Traefik evaluates router rules before decoding or normalizing the request path, but forwards the request after decoding to the backend service. As a result, routes meant to block access to sensitive endpoints (such as internal, beta, or admin endpoints) can be trivially bypassed.

### PoC
Traefik configuration used in this issue :
```[http.routers.flask-router-report-deny]
  entryPoints = ["web"]
  rule = "PathPrefix(`/report_note`)"
  priority = 10
  middlewares = ["block-access"]
  service = "flask-service"

[http.middlewares.block-access.replacePathRegex]
  regex = ".*"
  replacement = "/blocked"
```
The intention is to block all access to /report_note.

However, the following request bypasses the block:
```
POST /%2freport_note HTTP/1.1
Host: localhost:62814


```
### Impact
Access Control Bypass:
Any endpoint intended to be blocked (e.g., admin/debug/beta APIs) can be accessed by URL-encoding slashes or other characters.

This could lead to:

- Unauthorized access to restricted endpoints
- Execution of protected internal functionality
- Potential privilege escalation
- Bypass of security policies enforced via Traefik routing rules
</details>

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-gm3x-23wp-hc2c
- https://nvd.nist.gov/vuln/detail/CVE-2025-66490
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.32
- https://github.com/traefik/traefik/releases/tag/v3.6.4
