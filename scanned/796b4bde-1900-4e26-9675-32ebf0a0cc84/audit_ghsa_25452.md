# [H] Moodle uses predictable password-recovery tokens

## Summary
Severity: High
Advisory: GHSA-382v-gxj9-ffhc
CVE: CVE-2015-5267
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-382v-gxj9-ffhc
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.7.10
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.8
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.2

## Details
lib/moodlelib.php in Moodle through 2.6.11, 2.7.x before 2.7.10, 2.8.x before 2.8.8, and 2.9.x before 2.9.2 relies on the PHP mt_rand function to implement the random_string and complex_random_string functions, which makes it easier for remote attackers to predict password-recovery tokens via a brute-force approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5267
- https://github.com/moodle/moodle/commit/289bc7f9e3022918b4cfd2cc9851472f0cea2896
- https://github.com/moodle/moodle/commit/5337b2295237958c93b6c65fa595859aaa7bf257
- https://github.com/moodle/moodle/commit/6e8224365ffcdf328458ea7852dc62574e806119
- https://github.com/moodle/moodle/commit/e4ac3879c2d1f8fe66caa74ff1544248bccef61e
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=320291
- https://web.archive.org/web/20160323063809/http://www.securitytracker.com/id/1033619
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-50860
- http://www.openwall.com/lists/oss-security/2015/09/21/1
