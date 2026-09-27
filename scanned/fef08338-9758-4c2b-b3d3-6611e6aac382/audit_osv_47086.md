# [C] CVE-2015-8914

## Summary
Severity: Critical
Advisory: CVE-2015-8914
Aliases: GHSA-3vj4-cvjp-482h, PYSEC-2026-431
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2016-06-17
Source: https://osv.dev/vulnerability/CVE-2015-8914
Type: osv

## Details
The IPTables firewall in OpenStack Neutron before 7.0.4 and 8.0.0 through 8.1.0 allows remote attackers to bypass an intended ICMPv6-spoofing protection mechanism and consequently cause a denial of service or intercept network traffic via a link-local source address.

## References
- http://www.openwall.com/lists/oss-security/2016/06/10/5
- http://www.openwall.com/lists/oss-security/2016/06/10/6
- https://access.redhat.com/errata/RHSA-2016:1473
- https://access.redhat.com/errata/RHSA-2016:1474
- https://bugs.launchpad.net/neutron/+bug/1502933
- https://review.openstack.org/#/c/300233/
- https://review.openstack.org/#/c/310648/
- https://review.openstack.org/#/c/310652/
- https://security.openstack.org/ossa/OSSA-2016-009.html
- http://www.openwall.com/lists/oss-security/2016/06/10/5
- http://www.openwall.com/lists/oss-security/2016/06/10/6
- https://bugs.launchpad.net/neutron/+bug/1502933
