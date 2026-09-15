# [H] Containous Traefik Exposes Password Hashes

## Summary
Severity: High
Advisory: GHSA-r3fq-cmmw-cpmm
CVE: CVE-2019-12452
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-r3fq-cmmw-cpmm
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=1.7.0 <1.7.12

## Details
types/types.go in Containous Traefik 1.7.x through 1.7.11, when the `--api` flag is used and the API is publicly reachable and exposed without sufficient access control (which is contrary to the API documentation), allows remote authenticated users to discover password hashes by reading the Basic HTTP Authentication or Digest HTTP Authentication section, or discover a key by reading the ClientTLS section. These can be found in the JSON response to a `/api` request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12452
- https://github.com/containous/traefik/issues/4917
- https://github.com/containous/traefik/pull/4918
- https://github.com/traefik/traefik/commit/a169fec2e08e391d24b509c00fcf011656c1395c
- https://github.com/containous/traefik
