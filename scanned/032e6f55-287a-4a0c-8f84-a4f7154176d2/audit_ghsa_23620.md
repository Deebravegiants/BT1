# [M] Moodle reflected Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-3xh5-5v5v-mfgm
CVE: CVE-2019-14884
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-3xh5-5v5v-mfgm
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.3
- Packagist: `moodle/moodle` — affected >=3.6.0 <3.6.7
- Packagist: `moodle/moodle` — affected >=3.5.0 <3.5.9

## Details
A vulnerability was found in Moodle 3.7 before 3.7.3, 3.6 before 3.6.7 and 3.5 before 3.5.9, where a reflected XSS possible from some fatal error messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14884
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14884
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=393587#p1586751
