# [C] LiuOS vulnerable to Authorization Bypass through User-Controlled Key

## Summary
Severity: Critical
Advisory: CVE-2022-46179
Aliases: GHSA-f9x3-mj2r-cqmf
CVSS: 9.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H)
Published: 2022-12-28
Source: https://osv.dev/vulnerability/CVE-2022-46179
Type: osv

## Details
LiuOS is a small Python project meant to imitate the functions of a regular operating system. Version 0.1.0 and prior of LiuOS allow an attacker to set the GITHUB_ACTIONS environment variable to anything other than null or true and skip authentication checks. This issue is patched in the latest commit (c658b4f3e57258acf5f6207a90c2f2169698ae22) by requiring the var to be set to true, causing a test script to run instead of being able to login. A potential workaround is to check for the GITHUB_ACTIONS environment variable and set it to "" (no quotes) to null the variable and force credential checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46179.json
- https://github.com/LiuWoodsCode/LiuOS/security/advisories/GHSA-f9x3-mj2r-cqmf
- https://nvd.nist.gov/vuln/detail/CVE-2022-46179
- https://github.com/LiuWoodsCode/LiuOS/commit/c658b4f3e57258acf5f6207a90c2f2169698ae22
