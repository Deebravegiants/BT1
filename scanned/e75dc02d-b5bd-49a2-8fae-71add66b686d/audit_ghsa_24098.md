# [H] Gravity Forms plugin leak hashed passwords

## Summary
Severity: High
Advisory: GHSA-m983-q76g-cwpq
CVE: CVE-2020-13764
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m983-q76g-cwpq
Type: github-advisory

## Affected
- Packagist: `wp-premium/gravityforms` — affected >=0 <2.4.9

## Details
common.php in the Gravity Forms plugin before 2.4.9 for WordPress can leak hashed passwords because user_pass is not considered a special case for a `$current_user->get($property)` call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13764
- https://docs.gravityforms.com/gravityforms-change-log
- https://github.com/wp-premium/gravityforms
- https://github.com/wp-premium/gravityforms/compare/2.4.8...2.4.9
