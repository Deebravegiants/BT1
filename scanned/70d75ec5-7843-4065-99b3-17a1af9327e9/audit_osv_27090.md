# [H] HTTP Request Smuggling in netease-youdao/qanything

## Summary
Severity: High
Advisory: CVE-2024-10264
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10264
Type: osv

## Details
HTTP Request Smuggling vulnerability in netease-youdao/qanything version 1.4.1 allows attackers to exploit inconsistencies in the interpretation of HTTP requests between a proxy and a server. This can lead to unauthorized access, bypassing security controls, session hijacking, data leakage, and potentially arbitrary code execution.

## References
- https://huntr.com/bounties/988247d5-fd60-4d85-845a-e867d62c0d02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10264.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10264
