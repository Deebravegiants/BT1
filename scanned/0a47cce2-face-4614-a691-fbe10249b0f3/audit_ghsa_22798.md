# [M] Moodle vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-vm9c-39jx-q45w
CVE: CVE-2013-4522
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vm9c-39jx-q45w
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.3.10
- Packagist: `moodle/moodle` — affected >=2.4.0-beta <2.4.7
- Packagist: `moodle/moodle` — affected >=2.5.0-beta <2.5.3

## Details
lib/filelib.php in Moodle through 2.2.11, 2.3.x before 2.3.10, 2.4.x before 2.4.7, and 2.5.x before 2.5.3 does not send "Cache-Control: private" HTTP headers, which allows remote attackers to obtain sensitive information by requesting a file that had been previously retrieved by a caching proxy server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4522
- https://github.com/moodle/moodle/commit/d0041fb110201d3dc1a4546eca8b6108b440d1c5
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=244479
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-38743
- http://openwall.com/lists/oss-security/2013/11/25/1
