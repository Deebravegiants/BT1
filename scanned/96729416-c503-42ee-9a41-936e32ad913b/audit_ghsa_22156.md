# [M] OpenStack Identity Keystone Improper Access Control 

## Summary
Severity: Medium
Advisory: GHSA-f82m-w3p3-cgp3
CVE: CVE-2016-4911
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-f82m-w3p3-cgp3
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=9.0.0 <9.0.1

## Details
The Fernet Token Provider in OpenStack Identity (Keystone) 9.0.x before 9.0.1 (mitaka) allows remote authenticated users to prevent revocation of a chain of tokens and bypass intended access restrictions by rescoping a token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4911
- https://github.com/openstack/keystone/commit/0d376025bae61bf5ee19d992c7f336b99ac69240
- https://github.com/openstack/keystone/commit/ee1dc941042d1f71699971c5c30566af1b348572
- https://bugs.launchpad.net/keystone/+bug/1577558
- https://github.com/openstack/keystone
- https://github.com/pypa/advisory-database/tree/main/vulns/keystone/PYSEC-2016-38.yaml
- https://review.openstack.org/#/c/311886
- https://security.openstack.org/ossa/OSSA-2016-008.html
- http://www.openwall.com/lists/oss-security/2016/05/17/10
- http://www.openwall.com/lists/oss-security/2016/05/17/11
