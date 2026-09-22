# [M] Improper Access Control in danswer-ai/danswer

## Summary
Severity: Medium
Advisory: CVE-2024-7767
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-7767
Type: osv

## Details
An improper access control vulnerability exists in danswer-ai/danswer version v0.3.94. This vulnerability allows the first user created in the system to view, modify, and delete chats created by an Admin. This can lead to unauthorized access to sensitive information, loss of data integrity, and potential compliance violations.

## References
- https://huntr.com/bounties/1425dada-72d8-4bd9-a3e7-2863bb3e1a6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7767.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7767
