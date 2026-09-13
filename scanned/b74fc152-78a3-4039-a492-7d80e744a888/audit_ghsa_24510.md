# [M] OpenStack Identity Keystone is vulnerable to Block delegation escalation of privilege

## Summary
Severity: Medium
Advisory: GHSA-274v-r947-v34r
CVE: CVE-2014-3476
CWE: CWE-269
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-274v-r947-v34r
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Identity (Keystone) before 2013.2.4, 2014.1 before 2014.1.2, and Juno before Juno-2 does not properly handle chained delegation, which allows remote authenticated users to gain privileges by leveraging a (1) trust or (2) OAuth token with impersonation enabled to create a new token with additional roles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3476
- https://bugs.launchpad.net/keystone/+bug/1324592
- http://lists.opensuse.org/opensuse-security-announce/2014-06/msg00031.html
- http://secunia.com/advisories/57886
- http://secunia.com/advisories/59547
- http://www.openwall.com/lists/oss-security/2014/06/12/3
- http://www.securityfocus.com/bid/68026
