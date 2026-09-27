# [H] CVE-2024-57432

## Summary
Severity: High
Advisory: CVE-2024-57432
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2024-57432
Type: osv

## Details
macrozheng mall-tiny 1.0.1 suffers from Insecure Permissions. The application's JWT signing keys are hardcoded and do not change. User information is explicitly written into the JWT and used for subsequent privilege management, making it is possible to forge the JWT of any user to achieve authentication bypass.

## References
- https://github.com/peccc/restful_vul/blob/main/mall_tiny_weak_jwt/mall_tiny_weak_jwt.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57432.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57432
