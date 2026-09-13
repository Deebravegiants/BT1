# [M] RCE, Full Read SSRF, and Arbitrary File Read in infiniflow/ragflow

## Summary
Severity: Medium
Advisory: CVE-2024-12450
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12450
Type: osv

## Details
In infiniflow/ragflow versions 0.12.0, the `web_crawl` function in `document_app.py` contains multiple vulnerabilities. The function does not filter URL parameters, allowing attackers to exploit Full Read SSRF by accessing internal network addresses and viewing their content through the generated PDF files. Additionally, the lack of restrictions on the file protocol enables Arbitrary File Read, allowing attackers to read server files. Furthermore, the use of an outdated Chromium headless version with --no-sandbox mode enabled makes the application susceptible to Remote Code Execution (RCE) via known Chromium v8 vulnerabilities. These issues are resolved in version 0.14.0.

## References
- https://huntr.com/bounties/da06360c-87c3-4ba9-be67-29f6eff9d44a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12450.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12450
- https://github.com/infiniflow/ragflow/commit/3faae0b2c2f8a26233ee1442ba04874b3406f6e9
