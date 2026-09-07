# [M] Moodle Secure layout contained an insecure link in Boost theme

## Summary
Severity: Medium
Advisory: GHSA-pj45-hp8h-289r
CVE: CVE-2019-3851
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pj45-hp8h-289r
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.5
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.3

## Details
A vulnerability was found in moodle before versions 3.6.3 and 3.5.5. There was a link to site home within the the Boost theme's secure layout, meaning students could navigate out of the page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-3851
- https://github.com/moodle/moodle/commit/7f22b14efb3408645cede026ad11126f17e3f59a
- https://github.com/moodle/moodle/commit/911f7488068a56b05b0ad87be8f9e132075ab0a6
- https://github.com/moodle/moodle/commit/c430bed525c4c7e6e5a1c0f7222bc323cf9b6245
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3851
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=384014#p1547746
