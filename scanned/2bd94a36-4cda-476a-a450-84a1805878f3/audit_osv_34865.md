# [M] CVE-2025-65900

## Summary
Severity: Medium
Advisory: CVE-2025-65900
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-65900
Type: osv

## Details
Kalmia CMS version 0.2.0 contains an Incorrect Access Control vulnerability in the /kal-api/auth/users API endpoint. Due to insufficient permission validation and excessive data exposure in the backend, an authenticated user with basic read permissions can retrieve sensitive information for all platform users.

## References
- https://github.com/Noxurge/CVE-2025-65900/blob/main/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65900.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65900
- https://github.com/DifuseHQ/Kalmia
