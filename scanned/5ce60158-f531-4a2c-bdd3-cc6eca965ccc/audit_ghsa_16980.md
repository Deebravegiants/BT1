# [H] Buffer Overflow vulnerability in osrg gobgp

## Summary
Severity: High
Advisory: GHSA-6rqv-5cg7-m4x3
CVE: CVE-2023-46565
CWE: CWE-120
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-29
Source: https://github.com/advisories/GHSA-6rqv-5cg7-m4x3
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v3` — affected >=0

## Details
Buffer Overflow vulnerability in osrg gobgp commit 419c50dfac578daa4d11256904d0dc182f1a9b22 allows a remote attacker to cause a denial of service via the handlingError function in pkg/server/fsm.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46565
- https://github.com/osrg/gobgp/issues/2725
- https://github.com/osrg/gobgp/commit/419c50dfac578daa4d11256904d0dc182f1a9b22
- https://github.com/osrg/gobgp
