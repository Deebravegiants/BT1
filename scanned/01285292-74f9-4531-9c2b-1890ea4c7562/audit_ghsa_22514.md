# [M] Moodle allows attackers to obtain manager privileges

## Summary
Severity: Medium
Advisory: GHSA-454r-4cjv-vc9h
CVE: CVE-2015-5266
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-454r-4cjv-vc9h
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.10
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.8
- Packagist: `moodle/moodle` — affected >=2.9.0 <2.9.2

## Details
The enrol_meta_sync function in enrol/meta/locallib.php in Moodle through 2.6.11, 2.7.x before 2.7.10, 2.8.x before 2.8.8, and 2.9.x before 2.9.2 allows remote authenticated users to obtain manager privileges in opportunistic circumstances by leveraging incorrect role processing during a long-running sync script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5266
- https://github.com/moodle/moodle/commit/936facab28d8d8bd03f38da42cb80fafba1a06db
- https://github.com/moodle/moodle/commit/ab006d43e48add8e5495141d4d750c1531772ca2
- https://github.com/moodle/moodle/commit/dff6cdc88355f22ebaaf8f00c44a1ad51d272344
- https://github.com/moodle/moodle/commit/f7fbc80766b72ed1c9915698edd443ee8f6eafbd
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=320290
- https://web.archive.org/web/20160323063809/http://www.securitytracker.com/id/1033619
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-50744
- http://www.openwall.com/lists/oss-security/2015/09/21/1
