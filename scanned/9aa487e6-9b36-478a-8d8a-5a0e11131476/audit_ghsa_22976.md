# [H] OpenStack Identity Keystone and keystonemiddleware Insufficiently Protected Credentials

## Summary
Severity: High
Advisory: GHSA-8c4w-v65p-jvcv
CVE: CVE-2015-7546
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8c4w-v65p-jvcv
Type: github-advisory

## Affected
- PyPI: `keystone` — affected >=9.0.0.0b1 <9.0.0.0b2
- PyPI: `keystonemiddleware` — affected >=2.4.0 <4.1.0
- PyPI: `keystone` — affected >=8.0 <8.1.0
- PyPI: `keystonemiddleware` — affected >=0 <1.5.4
- PyPI: `keystonemiddleware` — affected >=1.6.0 <2.3.3

## Details
The identity service in OpenStack Identity (Keystone) before 2015.1.3 (Kilo) and 8.0.x before 8.0.2 (Liberty) and keystonemiddleware (formerly python-keystoneclient) before 1.5.4 (Kilo) and Liberty before 2.3.3 does not properly invalidate authorization tokens when using the PKI or PKIZ token providers, which allows remote authenticated users to bypass intended access restrictions and gain access to cloud resources by manipulating byte fields within a revoked token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7546
- https://github.com/openstack/keystone/commit/bff03b5726fe5cac93d44a66715eea49b89c8cb0
- https://github.com/openstack/keystone/commit/d5378f173da14a34ca010271477337879002d6d0
- https://github.com/openstack/keystonemiddleware/commit/96ab58e6863c92575ada57615b19652e502adfd8
- https://bugs.launchpad.net/keystone/+bug/1490804
- https://github.com/pypa/advisory-database/tree/main/vulns/keystonemiddleware/PYSEC-2016-20.yaml
- https://security.openstack.org/ossa/OSSA-2016-005.html
- https://web.archive.org/web/20200228002640/http://www.securityfocus.com/bid/80498
- https://wiki.openstack.org/wiki/OSSN/OSSN-0062
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
