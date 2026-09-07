# [M] Moodle does not recogniz configuration setting that makes e-mail addresses visible only to course members

## Summary
Severity: Medium
Advisory: GHSA-3qg4-2fcm-c8f9
CVE: CVE-2011-4289
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3qg4-2fcm-c8f9
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.3

## Details
Moodle 2.0.x before 2.0.3 does not recognize the configuration setting that makes e-mail addresses visible only to course members, which allows remote authenticated users to obtain sensitive address information by reading a full profile page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4289
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=181991e791a13a3c383234718c26c499e31d3df1
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=181991e791a13a3c383234718c26c499e31d3df1
- http://moodle.org/mod/forum/discuss.php?d=175591
- http://openwall.com/lists/oss-security/2011/11/14/1
