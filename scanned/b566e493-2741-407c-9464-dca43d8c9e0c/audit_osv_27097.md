# [H] IDOR in delete attachments in danny-avila/librechat

## Summary
Severity: High
Advisory: CVE-2024-10366
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10366
Type: osv

## Details
An improper access control vulnerability (IDOR) exists in the delete attachments functionality of danny-avila/librechat version v0.7.5-rc2. The endpoint does not verify whether the provided attachment ID belongs to the current user, allowing any authenticated user to delete attachments of other users.

## References
- https://huntr.com/bounties/cde47cf8-dc81-46ab-b472-f7e44a981a7e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10366.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10366
- https://github.com/danny-avila/librechat/commit/a350443661d001ac55787741969a75d94ca14116
