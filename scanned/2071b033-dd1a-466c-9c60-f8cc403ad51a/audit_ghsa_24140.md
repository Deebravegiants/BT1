# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wm4w-8vc6-2j4h
CVE: CVE-2019-3810
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-wm4w-8vc6-2j4h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.1
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.3
- Packagist: `moodle/moodle` — affected >=3.4.0 <3.4.6
- Packagist: `moodle/moodle` — affected >=3.1.0 <3.1.15

## Details
A flaw was found in moodle versions 3.6 to 3.6.1, 3.5 to 3.5.3, 3.4 to 3.4.6, 3.1 to 3.1.15 and earlier unsupported versions. The /userpix/ page did not escape users' full names, which are included as text when hovering over profile images. Note this page is not linked to by default and its access is restricted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3810
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3810
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=381230#p1536767
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-64372
- http://packetstormsecurity.com/files/162399/Moodle-3.6.1-Cross-Site-Scripting.html
