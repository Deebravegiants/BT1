# [M] Phar Deserialization leading to Arbitrary File Deletion in my little forum

## Summary
Severity: Medium
Advisory: CVE-2026-25923
Aliases: GHSA-wr9p-3c3g-78fw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25923
Type: osv

## Details
my little forum is a PHP and MySQL based internet forum that displays the messages in classical threaded view. Prior to 20260208.1, the application fails to filter the phar:// protocol in URL validation, allowing attackers to upload a malicious Phar Polyglot file (disguised as JPEG) via the image upload feature, trigger Phar deserialization through BBCode [img] tag processing, and exploit Smarty 4.1.0 POP chain to achieve arbitrary file deletion. This vulnerability is fixed in 20260208.1.

## References
- https://github.com/My-Little-Forum/mylittleforum/releases/tag/20260208.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25923.json
- https://github.com/My-Little-Forum/mylittleforum/security/advisories/GHSA-wr9p-3c3g-78fw
- https://nvd.nist.gov/vuln/detail/CVE-2026-25923
