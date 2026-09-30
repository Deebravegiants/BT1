# [M] Privilege Escalation in langgenius/dify

## Summary
Severity: Medium
Advisory: CVE-2024-11821
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11821
Type: osv

## Details
A privilege escalation vulnerability exists in langgenius/dify version 0.9.1. This vulnerability allows a normal user to modify Orchestrate instructions for a chatbot created by an admin user. The issue arises because the application does not properly enforce access controls on the endpoint /console/api/apps/{chatbot-id}/model-config, allowing unauthorized users to alter chatbot configurations.

## References
- https://huntr.com/bounties/76d5986d-3882-4ea7-81cb-f00400e5c6b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11821.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11821
