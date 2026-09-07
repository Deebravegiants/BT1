# [M] Moodle vulnerable to Cross-Site Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-m97f-x4mr-4x3q
CVE: CVE-2011-4281
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-m97f-x4mr-4x3q
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.2

## Details
Multiple cross-site request forgery (CSRF) vulnerabilities in Moodle 2.0.x before 2.0.2 allow remote attackers to hijack the authentication of arbitrary users for requests that mark the completion of (1) an activity or (2) a course.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4281
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=9cedb80c5d6318aa17cd66912d37e6ef3dca9455
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=9cedb80c5d6318aa17cd66912d37e6ef3dca9455
- http://moodle.org/mod/forum/discuss.php?d=170006
- http://openwall.com/lists/oss-security/2011/11/14/1
