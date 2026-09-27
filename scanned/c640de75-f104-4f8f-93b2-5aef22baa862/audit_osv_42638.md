# [H] SiYuan before v3.7.3 SQL Injection via fullTextSearchAssetContent

## Summary
Severity: High
Advisory: CVE-2026-69083
Aliases: GHSA-fph3-ghq9-vw66, GO-2026-6374
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69083
Type: osv

## Details
SiYuan versions before v3.7.3 contain SQL injection vulnerabilities in the fullTextSearchAssetContent endpoint reachable by unauthenticated users and publish RoleReader tokens. Attackers can execute arbitrary SQL on the read-write asset-content database via unescaped method parameters and REGEXP clauses to read, modify, or delete cross-notebook data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69083.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-fph3-ghq9-vw66
- https://nvd.nist.gov/vuln/detail/CVE-2026-69083
- https://www.vulncheck.com/advisories/siyuan-before-sql-injection-via-fulltextsearchassetcontent
