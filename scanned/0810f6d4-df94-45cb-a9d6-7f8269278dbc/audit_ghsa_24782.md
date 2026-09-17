# [H] OpenStack Nova Denial of service attack on the compute host

## Summary
Severity: High
Advisory: GHSA-ffmh-r67w-m88f
CVE: CVE-2017-18191
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-ffmh-r67w-m88f
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=15.0.0 <15.1.1
- PyPI: `nova` — affected >=16.0.0 <16.1.2

## Details
An issue was discovered in OpenStack Nova 15.x through 15.1.0 and 16.x through 16.1.1. By detaching and reattaching an encrypted volume, an attacker may access the underlying raw volume and corrupt the LUKS header, resulting in a denial of service attack on the compute host. (The same code error also results in data loss, but that is not a vulnerability because the user loses their own data.) All Nova setups supporting encrypted volumes are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18191
- https://github.com/openstack/nova/commit/0225a61fc4557c1257383a654f0741f7ef2ddeac
- https://github.com/openstack/nova/commit/5b64a1936122eeb35f37a09f9d38159e1a224c58
- https://github.com/openstack/nova/commit/cd3eb60c2c00bcccfa9ccd4bf9d1a96ae7a5cd88
- https://access.redhat.com/errata/RHSA-2018:2332
- https://access.redhat.com/errata/RHSA-2018:2714
- https://access.redhat.com/errata/RHSA-2018:2855
- https://github.com/openstack/nova
- https://launchpad.net/bugs/1739593
- https://review.openstack.org/539893
- https://security.openstack.org/ossa/OSSA-2018-001.html
- http://openwall.com/lists/oss-security/2018/04/20/3
- http://www.securityfocus.com/bid/103104
