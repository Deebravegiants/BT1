# [M] social-auth-app-django affected by Improper Handling of Case Sensitivity

## Summary
Severity: Medium
Advisory: GHSA-2gr8-3wc7-xhj3
CVE: CVE-2024-32879
CWE: CWE-178, CWE-303
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-2gr8-3wc7-xhj3
Type: github-advisory

## Affected
- PyPI: `social-auth-app-django` — affected >=0 <5.4.1

## Details
### Impact
Due to default case-insensitive collation in MySQL or MariaDB databases, third-party authentication user IDs are not case-sensitive and could cause different IDs to match.

### Patches
This issue has been addressed by https://github.com/python-social-auth/social-app-django/pull/566 and fix released in 5.4.1.

### Workarounds
An immediate workaround would be to change collation of the affected field:

```mysql
ALTER TABLE `social_auth_usersocialauth` MODIFY `uid` varchar(255) COLLATE `utf8_bin`;
```

### References
This issue was discovered by folks at https://opencraft.com/.

## References
- https://github.com/python-social-auth/social-app-django/security/advisories/GHSA-2gr8-3wc7-xhj3
- https://nvd.nist.gov/vuln/detail/CVE-2024-32879
- https://github.com/python-social-auth/social-app-django/pull/566
- https://github.com/python-social-auth/social-app-django/commit/31c3e0c7edb187004d8abbde7e9c4f7ef9098138
- https://github.com/python-social-auth/social-app-django
