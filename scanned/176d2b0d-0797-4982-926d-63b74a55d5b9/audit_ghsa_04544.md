# [H] Snipe-IT: Bulk editing users allowed `ldap_import` and `activated_in` bulk editing users

## Summary
Severity: High
Advisory: GHSA-6f75-x745-xcpr
CVE: CVE-2026-48507
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-6f75-x745-xcpr
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
The vulnerability allows a non-admin user holding only the granular `users.edit` permission to lock every admin out of the instance  by editing the `activated` flag (which determines whether or not a user can login) and the `ldap_import` flag, which determines whether or not the user can request a password reset.

### Patches
Patched in https://github.com/grokability/snipe-it/commit/403f9c848b05274642f64450696bdcdc242a352a

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-6f75-x745-xcpr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48507
- https://github.com/grokability/snipe-it/commit/403f9c848b05274642f64450696bdcdc242a352a
- https://github.com/grokability/snipe-it
- https://vokecyber.com/research/cve-2026-48507-snipe-it-admin-lockout
