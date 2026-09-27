# [H] Privilege Escalation in mintplex-labs/anything-llm

## Summary
Severity: High
Advisory: CVE-2024-0798
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-02-25
Source: https://osv.dev/vulnerability/CVE-2024-0798
Type: osv

## Details
A privilege escalation vulnerability exists in mintplex-labs/anything-llm, allowing users with 'default' role to delete documents uploaded by 'admin'. Despite the intended restriction that prevents 'default' role users from deleting admin-uploaded documents, an attacker can exploit this vulnerability by sending a crafted DELETE request to the /api/system/remove-document endpoint. This vulnerability is due to improper access control checks, enabling unauthorized document deletion and potentially leading to loss of data integrity.

## References
- https://huntr.com/bounties/607f03a0-ab4d-4905-b253-3d28bbbd363c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0798.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0798
- https://github.com/mintplex-labs/anything-llm/commit/d5cde8b7c27a47ab45b05b441db16751537f1733
