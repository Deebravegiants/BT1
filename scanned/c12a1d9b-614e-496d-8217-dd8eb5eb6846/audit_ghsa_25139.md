# [M] OpenStack Identity (Keystone) improper revoking of the authentication token when deleting a user 

## Summary
Severity: Medium
Advisory: GHSA-hj89-qmx9-8qmh
CVE: CVE-2013-2059
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hj89-qmx9-8qmh
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Identity (Keystone) Folsom 2012.2.4 and earlier, Grizzly before 2013.1.1, and Havana does not immediately revoke the authentication token when deleting a user through the Keystone v2 API, which allows remote authenticated users to retain access via the token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2059
- https://github.com/openstack/keystone/commit/33214f311aa36b17f8f5ff06bee2130bf061df8f
- https://github.com/openstack/keystone/commit/678b06a91f772d6be82eb54ed11f27e20f446b57
- https://github.com/openstack/keystone/commit/992466d1dbf80a940190703dedf800d6d12dede8
- https://bugs.launchpad.net/keystone/+bug/1166670
- https://exchange.xforce.ibmcloud.com/vulnerabilities/84135
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2013-41.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/105916.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-May/106220.html
- http://lists.opensuse.org/opensuse-updates/2013-06/msg00085.html
- http://www.openwall.com/lists/oss-security/2013/05/09/3
- http://www.openwall.com/lists/oss-security/2013/05/09/4
