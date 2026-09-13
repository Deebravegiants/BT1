# [M] SuiteCRM < 7.12.6 Type Confusion via 'deleteAttachment' Functionality

## Summary
Severity: Medium
Advisory: CVE-2022-50590
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2022-50590
Type: osv

## Details
SuiteCRM versions prior to 7.12.6 contain a type confusion vulnerability within the processing of the ‘module’ parameter within the ‘deleteAttachment’ functionality. Successful exploitation allows remote unauthenticated attackers to alter database objects including changing the email address of the administrator.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50590.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50590
- https://www.vulncheck.com/advisories/suitecrm-type-confusion-via-deleteattachment-functionality
- https://docs.suitecrm.com/admin/releases/7.12.x/#_7_12_6
- https://github.com/SuiteCRM/SuiteCRM
- https://blog.exodusintel.com/2022/06/09/salesagility-suitecrm-deleteattachment-type-confusion-vulnerability/
