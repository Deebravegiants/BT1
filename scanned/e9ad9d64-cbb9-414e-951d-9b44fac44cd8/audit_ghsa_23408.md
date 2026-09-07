# [M] Moodle Incorrect Default Settings

## Summary
Severity: Medium
Advisory: GHSA-8vjj-wf73-w882
CVE: CVE-2011-4285
CWE: CWE-276
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8vjj-wf73-w882
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0 <2.0.2

## Details
The default configuration of Moodle 2.0.x before 2.0.2 has an incorrect setting of the `moodle/course:delete` capability, which allows remote authenticated users to delete arbitrary courses by leveraging the teacher role.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4285
- https://github.com/moodle/moodle/commit/5dd7e903ff1698dcf2b6bbd821c31720d169fb83
- https://github.com/moodle/moodle
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=5cfe8aecb8b78e343ded38ba9e7a0a859887d21c
- http://moodle.org/mod/forum/discuss.php?d=170011
- http://openwall.com/lists/oss-security/2011/11/14/1
