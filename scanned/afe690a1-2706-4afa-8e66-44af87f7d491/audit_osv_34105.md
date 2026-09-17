# [C] FreshRSS: Unauthorized creation of admin user when registration is enabled

## Summary
Severity: Critical
Advisory: CVE-2025-54875
Aliases: GHSA-h625-ghr3-jppq
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-29
Source: https://osv.dev/vulnerability/CVE-2025-54875
Type: osv

## Details
FreshRSS is a free, self-hostable RSS aggregator. In versions 1.16.0 and above through 1.26.3, an unprivileged attacker can create a new admin user when registration is enabled through the use of a hidden field used only in the user management admin page, new_user_is_admin. This is fixed in version 1.27.0.

## References
- https://github.com/FreshRSS/FreshRSS/releases/tag/1.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54875.json
- https://github.com/FreshRSS/FreshRSS/security/advisories/GHSA-h625-ghr3-jppq
- https://nvd.nist.gov/vuln/detail/CVE-2025-54875
- https://github.com/FreshRSS/FreshRSS/pull/7783
