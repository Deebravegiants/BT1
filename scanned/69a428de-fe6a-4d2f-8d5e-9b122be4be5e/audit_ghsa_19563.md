# [H] Traefik has a possible vulnerability with its path matchers

## Summary
Severity: High
Advisory: GHSA-6p68-w45g-48j7
CVE: CVE-2025-32431
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-6p68-w45g-48j7
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.23
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.3.6
- Go: `github.com/traefik/traefik/v3` — affected >=3.4.0-rc1 <3.4.0-rc2

## Details
## Impact

There is a potential vulnerability in Traefik managing the requests using a `PathPrefix`, `Path` or `PathRegex` matcher.

When Traefik is configured to route the requests to a backend using a matcher based on the path, if the URL contains a `/../` in its path, it’s possible to target a backend, exposed using another router, by-passing the middlewares chain.

## Example

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-service
spec:
  routes:
    - match: PathPrefix(‘/service’)
      kind: Rule
      services:
        - name: service-a
          port: 8080
      middlewares:
        - name: my-middleware-a
    - match: PathPrefix(‘/service/sub-path’)
      kind: Rule
      services:
        - name: service-a
          port: 8080
```

In such a case, the request `http://mydomain.example.com/service/sub-path/../other-path` will reach the backend `my-service-a` without operating the middleware `my-middleware-a` unless the computed path is `http://mydomain.example.com/service/other-path` and should be computes by the first router (operating `my-middleware-a`).

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2

## Workaround

Add a `PathRegexp` rule to the matcher to prevent matching a route with a `/../` in the path.

Example: 

```yaml
match: PathPrefix(`/service`) && !PathRegexp(`(?:(/\.\./)+.*)`)
```

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6p68-w45g-48j7
- https://nvd.nist.gov/vuln/detail/CVE-2025-32431
- https://github.com/traefik/traefik/pull/11684
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2
