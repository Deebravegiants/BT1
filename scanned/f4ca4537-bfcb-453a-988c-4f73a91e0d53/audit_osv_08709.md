# [H] CVE-2016-5362

## Summary
Severity: High
Advisory: CVE-2016-5362
Aliases: GHSA-qpwc-p365-pqrr, PYSEC-2026-854
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-06-17
Source: https://osv.dev/vulnerability/CVE-2016-5362
Type: osv

## Details
The IPTables firewall in OpenStack Neutron before 7.0.4 and 8.0.0 through 8.1.0 allows remote attackers to bypass an intended DHCP-spoofing protection mechanism and consequently cause a denial of service or intercept network traffic via a crafted DHCP discovery message.

## References
- http://www.openwall.com/lists/oss-security/2016/06/10/5
- http://www.openwall.com/lists/oss-security/2016/06/10/6
- https://access.redhat.com/errata/RHSA-2016:1473
- https://access.redhat.com/errata/RHSA-2016:1474
- https://bugs.launchpad.net/neutron/+bug/1558658
- https://review.openstack.org/#/c/300202/
- https://review.openstack.org/#/c/303563/
- https://review.openstack.org/#/c/303572/
- https://security.openstack.org/ossa/OSSA-2016-009.html
