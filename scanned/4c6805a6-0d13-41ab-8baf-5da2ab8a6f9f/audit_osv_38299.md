# [M] CVE-2026-37505

## Summary
Severity: Medium
Advisory: CVE-2026-37505
CVSS: 4.9 (CVSS:3.1/AC:L/AV:N/A:N/C:H/I:N/PR:H/S:U/UI:N)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-37505
Type: osv

## Details
SQL Injection via ORDER BY clause in V2Board thru 1.7.4. In app/Http/Controllers/Admin/UserController.php, the sort parameter from user input is passed directly to User::orderBy($sort, $sortType) without validation. An authenticated admin can sort users by any database column including password, remember_token, and other sensitive fields, enabling information disclosure through ordering analysis.

## References
- https://gist.github.com/sgInnora/1330e1a82caa79906eec55eeff2c99b9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37505.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37505
- https://github.com/v2board/v2board
