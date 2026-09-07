# [M] Moodle exposes hidden grades to students

## Summary
Severity: Medium
Advisory: GHSA-59j6-8g7w-prf7
CVE: CVE-2014-7831
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-59j6-8g7w-prf7
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.3

## Details
lib/classes/grades_external.php in Moodle 2.7.x before 2.7.3 does not consider the moodle/grade:viewhidden capability before displaying hidden grades, which allows remote authenticated users to obtain sensitive information by leveraging the student role to access the get_grades web service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7831
- https://github.com/moodle/moodle/commit/3b8876f5ef2b5cde1e9de2599efd03d02bdaf7d8
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=275153
- https://web.archive.org/web/20150914064838/http://www.securitytracker.com/id/1031215
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-47766
- http://openwall.com/lists/oss-security/2014/11/17/11
