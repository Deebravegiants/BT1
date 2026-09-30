# [H] Traefik: HTTP/2 frames can cause a running server to panic

## Summary
Severity: High
Advisory: GHSA-4hjq-9h5c-252j
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-4hjq-9h5c-252j
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.40
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.10

## Details
## Summary

More Details:
- https://nvd.nist.gov/vuln/detail/CVE-2026-27141
- https://pkg.go.dev/golang.org/x/net/http2?tab=versions

## Patches

- https://github.com/traefik/traefik/releases/tag/v3.6.10
- https://github.com/traefik/traefik/releases/tag/v2.11.40

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-4hjq-9h5c-252j
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.40
- https://github.com/traefik/traefik/releases/tag/v3.6.10
