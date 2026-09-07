# [M] Moodle does not properly restrict comment capabilities

## Summary
Severity: Medium
Advisory: GHSA-62wv-866c-rh86
CVE: CVE-2011-4297
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-62wv-866c-rh86
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.4
- Packagist: `moodle/moodle` — affected >=2.1.0 <2.1.1

## Details
comment/lib.php in Moodle 2.0.x before 2.0.4 and 2.1.x before 2.1.1 does not properly restrict comment capabilities, which allows remote attackers to post a comment by leveraging the guest role and operating on a front-page activity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4297
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=9da3c2efadcc5f56cb8adc19c67ed16be35780f3
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=9da3c2efadcc5f56cb8adc19c67ed16be35780f3
- http://moodle.org/mod/forum/discuss.php?d=182740
- http://openwall.com/lists/oss-security/2011/11/14/1
