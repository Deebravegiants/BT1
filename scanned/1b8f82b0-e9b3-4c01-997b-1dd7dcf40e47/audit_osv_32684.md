# [H] XSS Vulnerability in langgenius/dify

## Summary
Severity: High
Advisory: CVE-2025-3467
CVSS: 8.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-07-07
Source: https://osv.dev/vulnerability/CVE-2025-3467
Type: osv

## Details
An XSS vulnerability exists in langgenius/dify versions prior to 1.1.3, specifically affecting Firefox browsers. This vulnerability allows an attacker to obtain the administrator's token by sending a payload in the published chat. When the administrator views the conversation content through the monitoring/log function using Firefox, the XSS vulnerability is triggered, potentially exposing sensitive token information to the attacker.

## References
- https://huntr.com/bounties/21723441-7b55-425c-abc4-b1331a713591
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/3xxx/CVE-2025-3467.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-3467
- https://github.com/langgenius/dify/commit/72deb3bed0b0d5d98d7cf44b525cc44bb278f6a7
