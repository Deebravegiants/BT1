# [M] Insufficient validation of bracketed IPv6 hostnames in net/url

## Summary
Severity: Medium
Advisory: BIT-golang-2025-47912
Aliases: CVE-2025-47912, GO-2025-4010
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-47912
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
The Parse function permits values other than IPv6 addresses to be included in square brackets within the host component of a URL. RFC 3986 permits IPv6 addresses to be included within the host component, enclosed within square brackets. For example: "http://[::1]/". IPv4 addresses and hostnames must not appear within square brackets. Parse did not enforce this requirement.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/709857
- https://go.dev/issue/75678
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-47912
- https://pkg.go.dev/vuln/GO-2025-4010
