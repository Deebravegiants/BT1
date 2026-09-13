# [M] OpenStack Keystone Logs Passwords

## Summary
Severity: Medium
Advisory: GHSA-jwpw-ppj5-7h4w
CVE: CVE-2015-3646
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-jwpw-ppj5-7h4w
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=2011.3 <2014.1.5
- PyPI: `keystone` — affected >=2014.2 <2014.2.4

## Details
OpenStack Identity (Keystone) before 2014.1.5 and 2014.2.x before 2014.2.4 logs the backend_argument configuration option content, which allows remote authenticated users to obtain passwords and other sensitive backend information by reading the Keystone logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3646
- https://bugs.launchpad.net/keystone/+bug/1443598
- https://github.com/openstack/keystone
- https://web.archive.org/web/20210122154200/http://www.securityfocus.com/bid/74456
- http://lists.openstack.org/pipermail/openstack-announce/2015-May/000356.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
