# [H] PenDoc vulnerable to Arbitrary File Read on updating and downloading templates using Path Traversal

## Summary
Severity: High
Advisory: CVE-2024-55602
Aliases: GHSA-2mqc-gg7h-76p6
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N)
Published: 2024-12-10
Source: https://osv.dev/vulnerability/CVE-2024-55602
Type: osv

## Details
PwnDoc is a penetration test report generator. Prior to commit 1d4219c596f4f518798492e48386a20c6e9a2fe6, an authenticated user who is able to update and download templates can inject path traversal (`../`) sequences into the file extension property to read arbitrary files on the system. Commit 1d4219c596f4f518798492e48386a20c6e9a2fe6 contains a patch for the issue.

## References
- https://gist.github.com/JorianWoltjer/8a42e25c6dfa7604020d2a226e193407
- https://github.com/pwndoc/pwndoc/blob/2e7f5747d5688b1368e549c786ce7266fe5ab2b5/backend/src/routes/template.js#L103
- https://github.com/pwndoc/pwndoc/blob/2e7f5747d5688b1368e549c786ce7266fe5ab2b5/backend/src/routes/template.js#L43-L47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55602.json
- https://github.com/pwndoc/pwndoc/security/advisories/GHSA-2mqc-gg7h-76p6
- https://nvd.nist.gov/vuln/detail/CVE-2024-55602
- https://github.com/pwndoc/pwndoc/commit/1d4219c596f4f518798492e48386a20c6e9a2fe6
