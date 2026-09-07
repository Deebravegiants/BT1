# [M] Moodle Exposes Sensitive User Information

## Summary
Severity: Medium
Advisory: GHSA-mr97-gvvg-rhgh
CVE: CVE-2012-2353
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mr97-gvvg-rhgh
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.1 <2.1.6
- Packagist: `moodle/moodle` — affected >=2.2 <2.2.3

## Details
Moodle 2.1.x before 2.1.6 and 2.2.x before 2.2.3 allows remote authenticated users to obtain sensitive user information from hidden fields by leveraging the teacher role and navigating to "Enrolled users" under the Users Settings section.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2353
- https://github.com/moodle/moodle/commit/a645b79113b2ee7881b6bdae64a0c2a9f04db5c7
- https://github.com/moodle/moodle/commit/ce13ea6ceb15f00c3cc6d40d79b06be39de7987a
- https://github.com/moodle/moodle/commit/cfaa50a61d61719c65aa7e26f5444852931e07b6
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-31923
- http://openwall.com/lists/oss-security/2012/05/23/2
