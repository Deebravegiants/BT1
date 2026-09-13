# [M] Traefik has an Improper Certificate Handling issue

## Summary
Severity: Medium
Advisory: GHSA-7h6j-2268-fhcm
CVE: CVE-2020-9321
CWE: CWE-200, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N/E:U/RL:O/RC:C (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-7h6j-2268-fhcm
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0 <2.1.4

## Details
configurationwatcher.go in Traefik 2.x before 2.1.4 and TraefikEE 2.0.0 mishandles the purging of certificate contents from providers before logging.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9321
- https://github.com/containous/traefik/pull/6281
- https://github.com/traefik/traefik/pull/6281
- https://github.com/containous/traefik/releases/tag/v2.1.4
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.1.4
