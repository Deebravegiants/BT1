# [H] OpenStack Keystone Domain-scoped tokens don't get revoked

## Summary
Severity: High
Advisory: GHSA-77w8-qv8m-386h
CVE: CVE-2014-5253
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-77w8-qv8m-386h
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Identity (Keystone) 2014.1.x before 2014.1.2.1 and Juno before Juno-3 does not properly revoke tokens when a domain is invalidated, which allows remote authenticated users to retain access via a domain-scoped token for that domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5253
- https://github.com/openstack/keystone/commit/317f9d34b4da20c21edd5b851889298b67c843e1
- https://github.com/openstack/keystone/commit/3e035ebb726167aef43c4a865c7e7f7d3b0978fb
- https://github.com/openstack/keystone/commit/c4447f16da036fe878382ce4e1b05b84bdcc4d4e
- https://github.com/openstack/keystone/commit/cccc3f3239c68479de0f6a41bd64badf2a9ec9e7
- https://bugs.launchpad.net/keystone/+bug/1349597
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2014-109.yaml
- http://rhn.redhat.com/errata/RHSA-2014-1121.html
- http://rhn.redhat.com/errata/RHSA-2014-1122.html
- http://www.openwall.com/lists/oss-security/2014/08/15/6
- http://www.ubuntu.com/usn/USN-2324-1
