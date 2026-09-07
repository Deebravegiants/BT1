# [H] Traefik affected by TLS ClientAuth Bypass on HTTP/3

## Summary
Severity: High
Advisory: GHSA-gv8r-9rw9-9697
CWE: CWE-1395
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-gv8r-9rw9-9697
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.37
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.8

## Details
### Summary

There is a potential vulnerability in Traefik managing HTTP/3 connections.

More details in the [CVE-2025-68121](https://nvd.nist.gov/vuln/detail/CVE-2025-68121).

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.37
- https://github.com/traefik/traefik/releases/tag/v3.6.8

## Workarounds

No workaround

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-gv8r-9rw9-9697
- https://github.com/traefik/traefik
