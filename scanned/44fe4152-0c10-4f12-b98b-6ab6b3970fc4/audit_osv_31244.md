# [H] Data Leak through CORS Misconfiguration in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-6674
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-6674
Type: osv

## Details
A CORS misconfiguration in parisneo/lollms-webui prior to version 10 allows attackers to steal sensitive information such as logs, browser sessions, and settings containing private API keys from other services. This vulnerability can also enable attackers to perform actions on behalf of a user, such as deleting a project or sending a message. The issue impacts the confidentiality and integrity of the information.

## References
- https://huntr.com/bounties/e688f71b-a3a4-4f6d-b48a-837073fa6908
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6674.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6674
- https://github.com/parisneo/lollms-webui/commit/c1bb1ad19752aa7541675b398495eaf98fd589f1
