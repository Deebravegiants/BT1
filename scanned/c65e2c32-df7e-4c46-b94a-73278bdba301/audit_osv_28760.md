# [H] CVE-2024-36267

## Summary
Severity: High
Advisory: CVE-2024-36267
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36267
Type: osv

## Details
Path traversal vulnerability exists in Redmine DMSF Plugin versions prior to 3.1.4. If this vulnerability is exploited, a logged-in user may obtain or delete arbitrary files on the server (within the privilege of the Redmine process).

## References
- https://jvn.jp/en/jp/JVN22182715/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36267.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36267
- https://github.com/danmunn/redmine_dmsf
