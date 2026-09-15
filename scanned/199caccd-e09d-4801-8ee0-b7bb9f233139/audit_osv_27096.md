# [M] Improper Access Control in danny-avila/LibreChat

## Summary
Severity: Medium
Advisory: CVE-2024-10363
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10363
Type: osv

## Details
In version 0.7.5 of danny-avila/LibreChat, there is an improper access control vulnerability. Users can share, use, and create prompts without being granted permission by the admin. This can break application logic and permissions, allowing unauthorized actions.

## References
- https://huntr.com/bounties/41a1137d-e725-4fec-b04c-58555cb16b6b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10363.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10363
- https://github.com/danny-avila/librechat/commit/42a4d02c62e2a6cf677d1cb6cfcb36d136aaa599
