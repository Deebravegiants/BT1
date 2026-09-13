# [H] Improper Authentication

## Summary
Severity: High
Advisory: GHSA-q9mp-79cp-9g8j
CVE: CVE-2019-20894
CWE: CWE-287, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-q9mp-79cp-9g8j
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.2.2

## Details
Traefik 2.x, in certain configurations, allows HTTPS sessions to proceed without mutual TLS verification in a situation where ERR_BAD_SSL_CLIENT_AUTH_CERT should have occurred.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20894
- https://github.com/containous/traefik/issues/5312
- https://github.com/containous/traefik/pull/7008
- https://github.com/containous/traefik/commit/2b353971696717e980521b0e4baa1eba66c8d2bf
