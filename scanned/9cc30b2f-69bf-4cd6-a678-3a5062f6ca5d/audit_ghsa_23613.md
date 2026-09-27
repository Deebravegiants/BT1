# [M] OpenStack Identity Keystone Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-c4p9-87h3-7vr4
CVE: CVE-2014-0204
CWE: CWE-269
Ecosystem: PyPI
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-c4p9-87h3-7vr4
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
OpenStack Identity (Keystone) before 2014.1.1 does not properly handle when a role is assigned to a group that has the same ID as a user, which allows remote authenticated users to gain privileges that are assigned to a group with the same ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0204
- https://github.com/openstack/keystone/commit/729dcad7384ba66ee7494154969cdd7ae90d86ee
- https://github.com/openstack/keystone/commit/786af9829c5329a982e3451f77afebbfb21850bd
- https://github.com/openstack/keystone/commit/97dfd55ad1b40365754dcbfce856f7ffae280a44
- https://github.com/openstack/keystone/commit/f0eee2f3b48dd0cffb9f75e396da2d914925cba5
- https://bugs.launchpad.net/keystone/+bug/1309228
- https://review.openstack.org/#/c/94396
- http://www.openwall.com/lists/oss-security/2014/05/21/3
