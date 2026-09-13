# [H] free5GC AMF denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-jcrr-rr6w-8c83
CVE: CVE-2023-49391
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-22
Source: https://github.com/advisories/GHSA-jcrr-rr6w-8c83
Type: github-advisory

## Affected
- Go: `github.com/free5gc/amf` — affected >=0

## Details
An issue was discovered in free5GC version 3.3.0, allows remote attackers to execute arbitrary code and cause a denial of service (DoS) on AMF component via crafted NGAP message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49391
- https://github.com/free5gc/free5gc/issues/497
- https://github.com/free5gc/amf/commit/6fc612c35997cf4e8be1e5c86ae2242f04b576a9
- https://github.com/free5gc/amf
