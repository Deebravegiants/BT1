# [H] Kanboard Authenticated SQL Injections vulnerability

## Summary
Severity: High
Advisory: CVE-2023-36813
Aliases: GHSA-9gvq-78jp-jxcx
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-36813
Type: osv

## Details
Kanboard is project management software that focuses on the Kanban methodology. In versions prior to 1.2.31authenticated user is able to perform a SQL Injection, leading to a privilege escalation or loss of confidentiality. It appears that in some insert and update operations, the code improperly uses the PicoDB library to update/insert new information. Version 1.2.31 contains a fix for this issue.

## References
- https://github.com/kanboard/kanboard/releases/tag/v1.2.31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36813.json
- https://github.com/kanboard/kanboard/security/advisories/GHSA-9gvq-78jp-jxcx
- https://nvd.nist.gov/vuln/detail/CVE-2023-36813
- https://www.debian.org/security/2023/dsa-5454
- https://github.com/kanboard/kanboard/commit/25b93343baeaf8ad018dcd87b094e47a5c6a3e0a
