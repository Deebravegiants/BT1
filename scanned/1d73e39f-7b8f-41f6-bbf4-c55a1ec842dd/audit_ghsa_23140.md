# [M] Moodle does not force password changes for autosubscribed users

## Summary
Severity: Medium
Advisory: GHSA-j3x5-cwfj-pfcw
CVE: CVE-2011-4287
CWE: CWE-263
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-j3x5-cwfj-pfcw
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.2

## Details
admin/uploaduser_form.php in Moodle 2.0.x before 2.0.3 does not force password changes for autosubscribed users, which makes it easier for remote attackers to obtain access by leveraging knowledge of the initial password of a new user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4287
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=22a77963439e00441949440f0517135b3a5418da
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=22a77963439e00441949440f0517135b3a5418da
- http://moodle.org/mod/forum/discuss.php?d=175588
- http://openwall.com/lists/oss-security/2011/11/14/1
