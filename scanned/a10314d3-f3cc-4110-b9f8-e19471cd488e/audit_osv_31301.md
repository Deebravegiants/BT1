# [C] Missing Authentication for Critical Function in mintplex-labs/anything-llm

## Summary
Severity: Critical
Advisory: CVE-2024-8196
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8196
Type: osv

## Details
In mintplex-labs/anything-llm v1.5.11 desktop version for Windows, the application opens server port 3001 on 0.0.0.0 with no authentication by default. This vulnerability allows an attacker to gain full backend access, enabling them to perform actions such as deleting all data from the workspace.

## References
- https://huntr.com/bounties/dbde1c71-7aa5-46f6-847a-d89793cf97a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8196.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8196
- https://github.com/mintplex-labs/anything-llm/commit/9bfe477f10b188bfe3508ac29105df80d4522ece
