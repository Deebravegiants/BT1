# [M] Improper Access Control in open-webui/open-webui

## Summary
Severity: Medium
Advisory: CVE-2024-7040
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-7040
Type: osv

## Details
In version v0.3.8 of open-webui/open-webui, there is an improper access control vulnerability. On the frontend admin page, administrators are intended to view only the chats of non-admin members. However, by modifying the user_id parameter, it is possible to view the chats of any administrator, including those of other admin (owner) accounts.

## References
- https://huntr.com/bounties/bd182309-4aa4-4747-941e-bbc1741955c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7040.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7040
