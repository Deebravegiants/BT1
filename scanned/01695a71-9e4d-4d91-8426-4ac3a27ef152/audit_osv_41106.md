# [H] Apache CXF: OAuth2 Authorization Code Replay via TOCTOU in JCacheCodeDataProvider

## Summary
Severity: High
Advisory: CVE-2026-57818
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-57818
Type: osv

## Details
A race condition in JCacheCodeDataProvider allows an attacker to redeem a single authorization code multiple times via concurrent requests, resulting in the issuance of multiple distinct, valid access tokens. Users are recommended to upgrade to versions 4.2.3, 4.1.8 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/06/20
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57818.json
- https://lists.apache.org/thread/7q08mz8bcbosp25wok7gr537zlp15mfz
- https://nvd.nist.gov/vuln/detail/CVE-2026-57818
