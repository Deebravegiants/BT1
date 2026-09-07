# [M] Moodle Information Disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wx87-h539-4775
CVE: CVE-2021-32473
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-wx87-h539-4775
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.18
- Packagist: `moodle/moodle` — affected >=3.8 <3.8.9
- Packagist: `moodle/moodle` — affected >=3.9 <3.9.7
- Packagist: `moodle/moodle` — affected >=3.10 <3.10.4

## Details
It was possible for a student to view their quiz grade before it had been released, using a quiz web service. Moodle 3.10 to 3.10.3, 3.9 to 3.9.6, 3.8 to 3.8.8, 3.5 to 3.5.17 and earlier unsupported versions are affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32473
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=422307
