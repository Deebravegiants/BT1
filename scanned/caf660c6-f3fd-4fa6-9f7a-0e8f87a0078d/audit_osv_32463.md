# [M] Emlog Pro contains an SQL injection vulnerability.

## Summary
Severity: Medium
Advisory: CVE-2025-30372
Aliases: GHSA-w6xc-r6x5-m77c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2025-30372
Type: osv

## Details
Emlog is an open source website building system. Emlog Pro versions pro-2.5.7 and pro-2.5.8 contain an SQL injection vulnerability. `search_controller.php` does not use addslashes after urldecode, allowing the preceeding addslashes to be bypassed by URL double encoding. This could result in potential leakage of sensitive information from the user database. Version pro-2.5.9 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30372.json
- https://github.com/emlog/emlog/security/advisories/GHSA-w6xc-r6x5-m77c
- https://nvd.nist.gov/vuln/detail/CVE-2025-30372
