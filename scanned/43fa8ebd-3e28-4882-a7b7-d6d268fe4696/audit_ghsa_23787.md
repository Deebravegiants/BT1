# [M] Moodle Reveals Student Information Meant To Be Anonymous

## Summary
Severity: Medium
Advisory: GHSA-2fmv-j5xj-4fmq
CVE: CVE-2014-0215
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-2fmv-j5xj-4fmq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.7.0
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.6
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.10

## Details
The blind-marking implementation in Moodle through 2.3.11, 2.4.x before 2.4.10, 2.5.x before 2.5.6, and 2.6.x before 2.6.3 allows remote authenticated users to de-anonymize student identities by (1) using a screen reader or (2) reading the HTML source.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0215
- https://moodle.org/mod/forum/discuss.php?d=260363
- http://openwall.com/lists/oss-security/2014/05/19/1
