# [M] Concrete CMS has a session-hardening bypass and allows password change without reauthorization

## Summary
Severity: Medium
Advisory: GHSA-wmw3-3fv3-h54w
CVE: CVE-2026-8327
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-wmw3-3fv3-h54w
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.5.1

## Details
Concrete CMS 9.5.0 and below is vulnerable to password change without reauthorization and session-hardening bypass. The user-profile edit controller passes the entire raw POST array to UserInfo::update() without field whitelisting resulting in password change without requiring the current password  and also resulting in registered users able to disable the per-user-IP-pinning in the session validator which is meant to detect hijacking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8327
- https://documentation.concretecms.org/9-x/developers/introduction/version-history/951-release-notes
- https://github.com/concretecms/concretecms
