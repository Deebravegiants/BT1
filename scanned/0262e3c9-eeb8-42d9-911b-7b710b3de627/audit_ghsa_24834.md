# [M] Moodle's time-validation implementation allows bypassing intended restrictions

## Summary
Severity: Medium
Advisory: GHSA-6p3g-hw27-qh44
CVE: CVE-2014-0127
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-6p3g-hw27-qh44
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.4.9
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.5
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.2

## Details
The time-validation implementation in (1) mod/feedback/complete.php and (2) mod/feedback/complete_guest.php in Moodle through 2.3.11, 2.4.x before 2.4.9, 2.5.x before 2.5.5, and 2.6.x before 2.6.2 allows remote authenticated users to bypass intended restrictions on starting a Feedback activity by choosing an unavailable time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0127
- https://github.com/moodle/moodle/commit/1298acc7075614d8f24befe7e50edbd695498d66
- https://github.com/moodle/moodle/commit/71037bf26c1e66c628f952b777a9b068775f7b24
- https://github.com/moodle/moodle/commit/7b839b0ec1d3d7fdfe7f76066c49829936a2390e
- https://github.com/moodle/moodle/commit/aea324963dfee857315d147bf0c17659bb43991e
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=256417
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-43656
- http://openwall.com/lists/oss-security/2014/03/17/1
