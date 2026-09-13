# [H] CVE-2025-70122

## Summary
Severity: High
Advisory: CVE-2025-70122
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70122
Type: osv

## Details
A heap buffer overflow vulnerability in the UPF component of free5GC v4.0.1 allows remote attackers to cause a denial of service via a crafted PFCP Session Modification Request. The issue occurs in the SDFFilterFields.UnmarshalBinary function (sdf-filter.go) when processing a declared length that exceeds the actual buffer capacity, leading to a runtime panic and UPF crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70122.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70122
- https://github.com/free5gc/free5gc/issues/746
