# [M] Moodle XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9jf6-wq34-fg9w
CVE: CVE-2019-14881
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9jf6-wq34-fg9w
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7.0 <3.7.3

## Details
A vulnerability was found in moodle 3.7 to 3.7.2 and before 3.7.3, where there is blind XSS reflected in some locations where user email is displayed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14881
- https://github.com/moodle/moodle/commit/7455b741c954af3c3e7dfda2972edc1146ea1562
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14881
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=393584#p1586746
