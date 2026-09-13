# [H] sysPass 3.2.11 Insecure Direct Object Reference via AccountFileController

## Summary
Severity: High
Advisory: CVE-2026-65708
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-65708
Type: osv

## Details
sysPass through version 3.2.11 contains an insecure direct object reference vulnerability that allows any authenticated attacker to access account file attachments belonging to accounts they do not have ACL permissions for by exploiting missing authorization checks in AccountFileController. Attackers can supply arbitrary numeric file IDs through the download, view, delete, upload, and list actions to enumerate and manipulate any attachment in the vault, bypassing account-level access controls entirely.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65708.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65708
- https://www.vulncheck.com/advisories/syspass-insecure-direct-object-reference-via-accountfilecontroller
- https://github.com/nuxsmin/sysPass
- https://github.com/Caycon/cve-advisories/blob/main/2026/sysPass/CVE-2026-65708.md
