# [C] CVE-2025-63679

## Summary
Severity: Critical
Advisory: CVE-2025-63679
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-63679
Type: osv

## Details
free5gc v4.1.0 and before is vulnerable to Buffer Overflow. When AMF receives an UplinkRANConfigurationTransfer NGAP message from a gNB, the AMF process crashes.

## References
- https://gist.github.com/DDGod2025/5483d94b028d7a0c111ca23844e8a94d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63679.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63679
- https://github.com/free5gc/free5gc/issues/725
