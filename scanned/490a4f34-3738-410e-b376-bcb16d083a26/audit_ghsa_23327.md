# [M] Moodle allows remote attackers to read arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-xmwv-mqh8-4xgw
CVE: CVE-2014-3542
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-xmwv-mqh8-4xgw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.11
- Packagist: `moodle/moodle` — affected >=2.5.0 <2.5.7
- Packagist: `moodle/moodle` — affected >=2.6.0 <2.6.4
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.1

## Details
mod/lti/service.php in Moodle through 2.3.11, 2.4.x before 2.4.11, 2.5.x before 2.5.7, 2.6.x before 2.6.4, and 2.7.x before 2.7.1 allows remote attackers to read arbitrary files via an XML external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3542
- https://github.com/moodle/moodle/commit/78ed99ec7e5e75b283e844adb058140d6ba0ff14
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=264263
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-45463
- http://openwall.com/lists/oss-security/2014/07/21/1
