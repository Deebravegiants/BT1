# [M] XADMaster may not apply quarantine attribute correctly to extracted files

## Summary
Severity: Medium
Advisory: CVE-2024-22405
Aliases: GHSA-xg3c-r7w5-7xw2
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2024-04-30
Source: https://osv.dev/vulnerability/CVE-2024-22405
Type: osv

## Details
XADMaster is an objective-C library for archive and file unarchiving and extraction. When extracting a specially crafted zip archive XADMaster may not apply quarantine attribute correctly. Such behaviour may circumvent Gatekeeper checks on the system. Only macOS installations are affected. This issue was fixed in XADMaster 1.10.8. It is recommended to upgrade to the latest version. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22405.json
- https://github.com/MacPaw/XADMaster/security/advisories/GHSA-xg3c-r7w5-7xw2
- https://nvd.nist.gov/vuln/detail/CVE-2024-22405
- https://github.com/MacPaw/XADMaster/commit/b75c05bc3bca9e183ecd3c512e270ce93006da3c
