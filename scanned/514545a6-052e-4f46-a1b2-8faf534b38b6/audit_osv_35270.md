# [H] CVE-2025-70121

## Summary
Severity: High
Advisory: CVE-2025-70121
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70121
Type: osv

## Details
An array index out of bounds vulnerability in the AMF component of free5GC v4.0.1 allows remote attackers to cause a denial of service via a crafted 5GS Mobile Identity in a NAS Registration Request message. The issue occurs in the GetSUCI method (NAS_MobileIdentity5GS.go) when accessing index 5 of a 5-element array, leading to a runtime panic and AMF crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70121.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70121
- https://github.com/free5gc/free5gc/issues/747
