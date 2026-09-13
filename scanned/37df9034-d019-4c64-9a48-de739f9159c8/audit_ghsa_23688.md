# [H] OpenStack Neutron Intended MAC-spoofing protection mechanism bypass

## Summary
Severity: High
Advisory: GHSA-9pp3-cvmq-9p22
CVE: CVE-2016-5363
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9pp3-cvmq-9p22
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0 <7.1.0
- PyPI: `neutron` — affected >=8.0.0 <8.1.0

## Details
The IPTables firewall in OpenStack Neutron up to 7.0.4 and 8.x before 8.1.0 allows remote attackers to bypass an intended MAC-spoofing protection mechanism and consequently cause a denial of service or intercept network traffic via (1) a crafted DHCP discovery message or (2) crafted non-IP traffic.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-5363
- https://github.com/openstack/neutron/commit/5853af9cba6733725d6c9ac0db644f426713f0cf
- https://github.com/openstack/neutron/commit/6a93ee8ac1a901c255e3475a24f1afc11d8bf80f
- https://github.com/openstack/neutron/commit/997d7b03fb7f5528f0a3ce70867b9dcd9321509e
- https://github.com/openstack/neutron/commit/fd5fd259a02156babdfcb12f66cde6ec9e7274ae
- https://access.redhat.com/errata/RHSA-2016:1473
- https://access.redhat.com/errata/RHSA-2016:1474
- https://bugs.launchpad.net/neutron/+bug/1558658
- https://github.com/openstack/neutron
- https://review.openstack.org/#/c/299021
- https://review.openstack.org/#/c/299023
- https://review.openstack.org/#/c/299025
- https://security.openstack.org/ossa/OSSA-2016-009.html
- http://www.openwall.com/lists/oss-security/2016/06/10/5
- http://www.openwall.com/lists/oss-security/2016/06/10/6
