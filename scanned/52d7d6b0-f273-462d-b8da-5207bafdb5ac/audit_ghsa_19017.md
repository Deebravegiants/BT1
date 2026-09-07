# [M] Free5GC is vulnerable to DoS through its Npcf_BDTPolicyControl POST API

## Summary
Severity: Medium
Advisory: GHSA-vgq7-9r5r-j9v3
CVE: CVE-2025-60632
CWE: CWE-617
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-vgq7-9r5r-j9v3
Type: github-advisory

## Affected
- Go: `github.com/free5gc/pcf` — affected >=0 <1.4.0

## Details
An issue was discovered in Free5GC v4.0.0 and v4.0.1 allowing an attacker to cause a denial of service via crafted POST request to the Npcf_BDTPolicyControl API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60632
- https://github.com/free5gc/free5gc/issues/705
- https://github.com/free5gc/pcf/pull/53
- https://github.com/free5gc/free5gc
- https://github.com/free5gc/pcf
