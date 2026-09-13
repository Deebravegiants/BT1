# [H] Regular Expression Denial of Service in hawk

## Summary
Severity: High
Advisory: GHSA-jcpv-g9rr-qxrc
CVE: CVE-2016-2515
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-jcpv-g9rr-qxrc
Type: github-advisory

## Affected
- npm: `hawk` — affected >=4.0.0 <4.1.1
- npm: `hawk` — affected >=0 <3.1.3

## Details
Versions of `hawk` prior to 3.1.3, or 4.x prior to 4.1.1 are affected by a regular expression denial of service vulnerability related to excessively long headers and URI's.



## Recommendation

Update to hawk version 4.1.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2515
- https://github.com/hueniverse/hawk/issues/168
- https://github.com/hueniverse/hawk/commit/0833f99ba64558525995a7e21d4093da1f3e15fa
- https://bugzilla.redhat.com/show_bug.cgi?id=1309721
- https://github.com/advisories/GHSA-jcpv-g9rr-qxrc
- https://github.com/hueniverse/hawk
- https://www.npmjs.com/advisories/77
- http://www.openwall.com/lists/oss-security/2016/02/20/1
- http://www.openwall.com/lists/oss-security/2016/02/20/2
