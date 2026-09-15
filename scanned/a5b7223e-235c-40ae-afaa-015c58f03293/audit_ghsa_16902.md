# [M] Traefik affected by HTTP/2 CONTINUATION flood in net/http

## Summary
Severity: Medium
Advisory: GHSA-7f4j-64p6-5h5v
Ecosystem: Go
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-7f4j-64p6-5h5v
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-rc1 <3.0.0-rc5

## Details
There is a potential vulnerability in Traefik managing HTTP/2 connections.

More details in the [CVE-2023-45288](https://www.cve.org/CVERecord?id=CVE-2023-45288).

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.2
- https://github.com/traefik/traefik/releases/tag/v3.0.0-rc5

## Workarounds

No workaround

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-7f4j-64p6-5h5v
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.2
- https://github.com/traefik/traefik/releases/tag/v3.0.0-rc5
