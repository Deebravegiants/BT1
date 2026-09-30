# [H] Traefik affected by Go oauth2/jws Improper Validation of Syntactic Correctness of Input vulnerability

## Summary
Severity: High
Advisory: GHSA-3wqc-mwfx-672p
CWE: CWE-1286
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-18
Source: https://github.com/advisories/GHSA-3wqc-mwfx-672p
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.3.6
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.24
- Go: `github.com/traefik/traefik/v3` — affected >=3.4.0-rc1 <3.4.0-rc2

## Details
### Summary
We have encountered a security vulnerability being reported by our scanners for Traefik 2.11.22.
- https://security.snyk.io/vuln/SNYK-CHAINGUARDLATEST-TRAEFIK33-9403297

### Details
It seems to target oauth2/jws library.

### PoC
No steps to replicate this vulnerability

### Impact
We have a strict control on security and we always try to stay up-to-date with the fixes received for third-party solutions.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-3wqc-mwfx-672p
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.24
- https://github.com/traefik/traefik/releases/tag/v3.3.6
- https://github.com/traefik/traefik/releases/tag/v3.4.0-rc2
- https://security.snyk.io/vuln/SNYK-CHAINGUARDLATEST-TRAEFIK33-9403297
