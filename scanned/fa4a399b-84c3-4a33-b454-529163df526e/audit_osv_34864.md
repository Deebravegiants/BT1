# [M] CVE-2025-65899

## Summary
Severity: Medium
Advisory: CVE-2025-65899
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-65899
Type: osv

## Details
Kalmia CMS version 0.2.0 contains a user enumeration vulnerability in its authentication mechanism. The application returns different error messages for invalid users (user_not_found) versus valid users with incorrect passwords (invalid_password). This observable response discrepancy allows unauthenticated attackers to enumerate valid usernames on the system.

## References
- https://github.com/Noxurge/CVE-2025-65899/blob/main/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65899.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65899
- https://github.com/DifuseHQ/Kalmia
