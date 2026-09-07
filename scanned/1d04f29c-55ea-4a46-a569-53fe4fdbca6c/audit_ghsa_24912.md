# [M] Moodle does not use the forceloginforprofiles setting for course-profiles access control

## Summary
Severity: Medium
Advisory: GHSA-phqj-xp48-7p7c
CVE: CVE-2011-4279
CWE: CWE-200, CWE-284
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-phqj-xp48-7p7c
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0 <2.0.2

## Details
Moodle 2.0.x before 2.0.2 does not use the forceloginforprofiles setting for course-profiles access control, which makes it easier for remote attackers to obtain potentially sensitive information via vectors involving use of a search engine, as demonstrated by the search functionality of Google, Yahoo!, Wrensoft Zoom, MSN, Yandex, and AltaVista.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4279
- http://git.moodle.org
- http://git.moodle.org/gw?p=moodle.git%3Ba=commit%3Bh=81b58cc227cf96a1cd2e002cc210b7b3e376fd17
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=81b58cc227cf96a1cd2e002cc210b7b3e376fd17
- http://moodle.org/mod/forum/discuss.php?d=170004
- http://openwall.com/lists/oss-security/2011/11/14/1
