# [M] Moodle vulnerable to symlink attack

## Summary
Severity: Medium
Advisory: GHSA-x7r4-26m9-hmgq
CVE: CVE-2008-5153
CWE: CWE-59
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x7r4-26m9-hmgq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=1.9.0 <1.9.4
- Packagist: `moodle/moodle` — affected >=1.8.0 <1.8.8
- Packagist: `moodle/moodle` — affected >=1.7.0 <1.7.7
- Packagist: `moodle/moodle` — affected >=1.6.0 <1.6.9

## Details
`spell-check-logic.cgi` in Moodle 1.9 before 1.9.4, 1.8 before 1.8.8, 1.7 before 1.7.7 and 1.6 before 1.6.9 allows local users to overwrite arbitrary files via a symlink attack on the (1) `/tmp/spell-check-debug.log`, (2) `/tmp/spell-check-before`, or (3) `/tmp/spell-check-after` temporary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-5153
- https://exchange.xforce.ibmcloud.com/vulnerabilities/46708
- https://github.com/moodle/moodle
- https://web.archive.org/web/20090821033319/http://secunia.com/advisories/33955
- https://web.archive.org/web/20110511083352/http://uvw.ru/report.sid.txt
- https://web.archive.org/web/20141121115305/http://www.securityfocus.com/bid/32402
- http://lists.debian.org/debian-devel/2008/08/msg00347.html
- http://www.debian.org/security/2009/dsa-1724
