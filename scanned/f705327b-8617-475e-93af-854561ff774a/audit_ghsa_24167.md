# [M] Moodle does not properly implement group-based access restrictions

## Summary
Severity: Medium
Advisory: GHSA-gmhr-6f43-7qpj
CVE: CVE-2015-5339
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gmhr-6f43-7qpj
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.11
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.9
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.3

## Details
The core_enrol_get_enrolled_users web service in enrol/externallib.php in Moodle through 2.6.11, 2.7.x before 2.7.11, 2.8.x before 2.8.9, and 2.9.x before 2.9.3 does not properly implement group-based access restrictions, which allows remote authenticated users to obtain sensitive course-participant information via a web-service request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5339
- https://github.com/moodle/moodle/commit/12bc713081dc24b6eedea54281876e7c3f5579a6
- https://github.com/moodle/moodle/commit/512633461ae239677342b40d318803e15e1fd1aa
- https://github.com/moodle/moodle/commit/b26b2407908abb1a8a4d37aebc18e03139c9776f
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=323234
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-51861
