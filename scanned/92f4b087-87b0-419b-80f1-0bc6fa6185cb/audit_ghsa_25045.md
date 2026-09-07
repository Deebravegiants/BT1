# [M] Moodle includes the WebDAV password in the configuration form

## Summary
Severity: Medium
Advisory: GHSA-pgp5-rcwp-qvfg
CVE: CVE-2013-1832
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-pgp5-rcwp-qvfg
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.0.0
- Packagist: `moodle/moodle` — affected >=2.2.0 <2.2.8
- Packagist: `moodle/moodle` — affected >=2.3.0 <2.3.5
- Packagist: `moodle/moodle` — affected >=2.4.0 <2.4.2

## Details
repository/webdav/lib.php in Moodle 2.x through 2.1.10, 2.2.x before 2.2.8, 2.3.x before 2.3.5, and 2.4.x before 2.4.2 includes the WebDAV password in the configuration form, which allows remote authenticated administrators to obtain sensitive information by configuring an instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1832
- https://github.com/moodle/moodle/commit/0e94caf991d4e399726e5dc0769873d9f753a727
- https://github.com/moodle/moodle/commit/46eec6e46b89a7e8e3f08e460d917f2d1a2959d8
- https://github.com/moodle/moodle/commit/92e592385784ec7ea5b5328a0c3c1608d321ad32
- https://github.com/moodle/moodle/commit/ce96f23fe15ce6addc2f56af015452c3ea406190
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=225343
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-37681
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101310.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-April/101358.html
- http://openwall.com/lists/oss-security/2013/03/25/2
