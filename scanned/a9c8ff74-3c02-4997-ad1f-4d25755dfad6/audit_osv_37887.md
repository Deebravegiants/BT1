# [M] Chamilo LMS Critical IDOR: Any Authenticated User Can Extract All Users’ Personal Data and API Tokens

## Summary
Severity: Medium
Advisory: CVE-2026-33703
Aliases: GHSA-27x6-c5c7-gpf5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-33703
Type: osv

## Details
Chamilo LMS is a learning management system. Prior to 2.0.0-RC.3, an Insecure Direct Object Reference (IDOR) vulnerability in the /social-network/personal-data/{userId} endpoint allows any authenticated user to access full personal data and API tokens of arbitrary users by modifying the userId parameter. This results in mass disclosure of sensitive user information and credentials, enabling a full platform data breach. This vulnerability is fixed in 2.0.0-RC.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33703.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-27x6-c5c7-gpf5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33703
