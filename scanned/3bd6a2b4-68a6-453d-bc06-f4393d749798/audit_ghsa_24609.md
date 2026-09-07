# [H] Moodle Login CSRF vulnerability in login form

## Summary
Severity: High
Advisory: GHSA-xj5f-qv37-r9jc
CVE: CVE-2018-16854
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xj5f-qv37-r9jc
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.1 <3.1.15
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.9
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.6
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.3

## Details
A flaw was found in moodle versions 3.5 to 3.5.2, 3.4 to 3.4.5, 3.3 to 3.3.8, 3.1 to 3.1.14 and earlier. The login form is not protected by a token to prevent login cross-site request forgery. Fixed versions include 3.6, 3.5.3, 3.4.6, 3.3.9 and 3.1.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16854
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16854
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=378731
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-63183
- http://www.securityfocus.com/bid/106017
- http://www.securitytracker.com/id/1042154
