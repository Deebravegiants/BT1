# [H] NSSF panic due to nil pointer dereference when expiry field is omitted in NSSAIAvailability POST

## Summary
Severity: High
Advisory: GHSA-f2hj-vpp9-6vm2
CVE: CVE-2025-60638
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-f2hj-vpp9-6vm2
Type: github-advisory

## Affected
- Go: `github.com/free5gc/nssf` — affected >=0 <1.4.0

## Details
An issue was discovered in Free5GC v4.0.0 and v4.0.1 allowing an attacker to cause a denial of service via crafted POST request to the Nnssf_NSSAIAvailability API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60638
- https://github.com/free5gc/free5gc/issues/704
- https://github.com/free5gc/nssf/commit/66fc727a894fa821fde14030346b18de69192204
- https://github.com/free5gc/free5gc
- https://github.com/free5gc/nssf
