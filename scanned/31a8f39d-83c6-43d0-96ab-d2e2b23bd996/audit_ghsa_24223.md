# [H] Traefik Missing Authentication

## Summary
Severity: High
Advisory: GHSA-2cjc-rgmp-x649
CVE: CVE-2018-15598
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2cjc-rgmp-x649
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=1.6.0 <1.6.6

## Details
Containous Traefik 1.6.x before 1.6.6, when `--api` is used, exposes the configuration and secret if authentication is missing and the API's port is publicly reachable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15598
- https://github.com/containous/traefik/pull/3790
- https://github.com/containous/traefik/commit/113250ce5735d554c502ca16fb03bb9119ca79f1
- https://github.com/containous/traefik/commit/368bd170913078732bde58160f92f202f370278b
- https://github.com/containous/traefik
- https://github.com/containous/traefik/releases/tag/v1.6.6
