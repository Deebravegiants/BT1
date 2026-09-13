# [H] CVE-2025-70866

## Summary
Severity: High
Advisory: CVE-2025-70866
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2025-70866
Type: osv

## Details
LavaLite CMS 10.1.0 is vulnerable to Incorrect Access Control. An authenticated user with low-level privileges (User role) can directly access the admin backend by logging in through /admin/login. The vulnerability exists because the admin and user authentication guards share the same user provider without role-based access control verification.

## References
- https://gist.github.com/gkjzjh146/6d541c80b0666a596581ccd85bd10058
- https://github.com/LavaLite/cms/releases/tag/v10.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70866.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70866
