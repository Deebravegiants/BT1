# [M] bbPress stored Cross-Site Scripting (XSS) vulnerability in the Forum creation section

## Summary
Severity: Medium
Advisory: GHSA-p9xp-xghp-gqvp
CVE: CVE-2020-13487
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p9xp-xghp-gqvp
Type: github-advisory

## Affected
- Packagist: `bbpress/bbpress` — affected >=0

## Details
The bbPress plugin through 2.6.4 for WordPress has stored XSS in the Forum creation section, resulting in JavaScript execution at wp-admin/edit.php?post_type=forum (aka the Forum listing page) for all users. An administrator can exploit this at the wp-admin/post.php?action=edit URI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13487
- https://bbpress.org
- https://codex.bbpress.org/releases
- https://github.com/bbpress/bbPress
- https://wordpress.org/plugins/bbpress/#developers
- https://www.youtube.com/watch?v=3rXP8CGTe08
