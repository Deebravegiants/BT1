# [H] sysPass 3.2.11 Missing Object-Level Authorization via JSON-RPC API

## Summary
Severity: High
Advisory: CVE-2026-65709
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-65709
Type: osv

## Details
sysPass through version 3.2.11 contains a missing object-level authorization vulnerability in the JSON-RPC API that allows API token holders to enumerate account metadata, overwrite passwords, and delete accounts across the entire vault without per-account access control. Attackers can invoke AccountController methods such as viewAction, editAction, deleteAction, and editPassAction without AccountFilterUser checks to modify or delete accounts beyond the scope of their assigned token permissions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65709.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65709
- https://www.vulncheck.com/advisories/syspass-missing-object-level-authorization-via-json-rpc-api
- https://github.com/nuxsmin/sysPass
- https://github.com/Caycon/cve-advisories/blob/main/2026/sysPass/CVE-2026-65709.md
