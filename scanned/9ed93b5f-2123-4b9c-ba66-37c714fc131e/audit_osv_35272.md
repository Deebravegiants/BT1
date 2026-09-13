# [H] CVE-2025-70123

## Summary
Severity: High
Advisory: CVE-2025-70123
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70123
Type: osv

## Details
An improper input validation and protocol compliance vulnerability in free5GC v4.0.1 allows remote attackers to cause a denial of service. The UPF incorrectly accepts a malformed PFCP Association Setup Request, violating 3GPP TS 29.244. This places the UPF in an inconsistent state where a subsequent valid PFCP Session Establishment Request triggers a cascading failure, disrupting the SMF connection and causing service degradation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70123.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70123
- https://github.com/free5gc/free5gc/issues/745
