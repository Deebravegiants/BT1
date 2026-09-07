# [H] Moodle Improper Authentication

## Summary
Severity: High
Advisory: GHSA-qh8m-6g4p-33h3
CVE: CVE-2018-1082
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qh8m-6g4p-33h3
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.3 <3.3.5
- Packagist: `moodle/moodle` — affected >=3.4 <3.4.2

## Details
A flaw was found in Moodle 3.4 to 3.4.1, and 3.3 to 3.3.4. If a user account using OAuth2 authentication method was once confirmed but later suspended, the user could still login to the site.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1082
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=367939
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-60101
- http://www.securityfocus.com/bid/103725
