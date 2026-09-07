# [M] Moodle Cross-site scripting (XSS) vulnerability in course management search

## Summary
Severity: Medium
Advisory: GHSA-gj2j-ppjq-9pjg
CVE: CVE-2016-0725
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gj2j-ppjq-9pjg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.8 <2.8.10
- Packagist: `moodle/moodle` — affected >=2.9 <2.9.4
- Packagist: `moodle/moodle` — affected >=3.0 <3.0.2

## Details
Cross-site scripting (XSS) vulnerability in the search_pagination function in course/classes/management_renderer.php in Moodle 2.8.x before 2.8.10, 2.9.x before 2.9.4, and 3.0.x before 3.0.2 allows remote attackers to inject arbitrary web script or HTML via a crafted search string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0725
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=326206
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-52552
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176502.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176436.html
- http://www.openwall.com/lists/oss-security/2016/01/18/1
- http://www.securitytracker.com/id/1034694
