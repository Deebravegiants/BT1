# [H] free5GC udm vulnerable to Invalid Curve Attack

## Summary
Severity: High
Advisory: GHSA-cqvv-r3g3-26rf
CVE: CVE-2023-46324
CWE: CWE-327, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-23
Source: https://github.com/advisories/GHSA-cqvv-r3g3-26rf
Type: github-advisory

## Affected
- Go: `github.com/free5gc/udm` — affected >=0 <1.2.0

## Details
pkg/suci/suci.go in free5GC udm before 1.2.0, when Go before 1.19 is used, allows an Invalid Curve Attack because it may compute a shared secret via an uncompressed public key that has not been validated. An attacker can send arbitrary SUCIs to the UDM, which tries to decrypt them via both its private key and the attacker's public key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46324
- https://github.com/free5gc/udm/pull/20
- https://github.com/free5gc/udm/commit/5e1479cc686f058992557669b13fd3761a1b6024
- https://github.com/free5gc/udm
- https://github.com/free5gc/udm/compare/v1.1.1...v1.2.0
- https://www.gsma.com/security/wp-content/uploads/2023/10/0073-invalid_curve.pdf
