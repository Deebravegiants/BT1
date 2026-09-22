# [M] ZimaOS  Privilege Escalation using localhost calls to File API Upload

## Summary
Severity: Medium
Advisory: CVE-2025-58432
Aliases: GHSA-3gp9-43rg-xrcc
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-58432
Type: osv

## Details
ZimaOS is a fork of CasaOS, an operating system for Zima devices and x86-64 systems with UEFI. In version 1.4.1 and all prior versions, the /v2_1/files/file/uploadV2 endpoint allows file upload from ANY USER who has access to localhost. File uploads are performed AS ROOT.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58432.json
- https://github.com/IceWhaleTech/ZimaOS/security/advisories/GHSA-3gp9-43rg-xrcc
- https://nvd.nist.gov/vuln/detail/CVE-2025-58432
