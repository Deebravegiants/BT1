# [H] DataEase's DB2 is vulnerable to SSRF

## Summary
Severity: High
Advisory: CVE-2025-64163
Aliases: GHSA-8397-v66p-539m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N/E:P)
Published: 2025-11-05
Source: https://osv.dev/vulnerability/CVE-2025-64163
Type: osv

## Details
DataEase is an open source data visualization analysis tool. In versions 2.10.14 and below, the vendor added a blacklist to filter ldap:// and ldaps://. However, omission of protection for the dns:// protocol results in an SSRF vulnerability. This issue is fixed in version 2.10.15.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64163.json
- https://github.com/dataease/dataease/security/advisories/GHSA-8397-v66p-539m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64163
- https://github.com/dataease/dataease/commit/869b7fb8b10069ac6c326554bfa8f060a539ba85
