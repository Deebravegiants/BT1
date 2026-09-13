# [H] Cross-Site WebSocket Hijacking in binary-husky/gpt_academic

## Summary
Severity: High
Advisory: CVE-2024-10956
CVSS: 7.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10956
Type: osv

## Details
GPT Academy version 3.83 in the binary-husky/gpt_academic repository is vulnerable to Cross-Site WebSocket Hijacking (CSWSH). This vulnerability allows an attacker to hijack an existing WebSocket connection between the victim's browser and the server, enabling unauthorized actions such as deleting conversation history without the victim's consent. The issue arises due to insufficient WebSocket authentication and lack of origin validation.

## References
- https://huntr.com/bounties/0f8403ad-5f60-4eb9-9f51-8fbd2e41eda4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10956.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10956
