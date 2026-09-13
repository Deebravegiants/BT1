# [H] CVE-2016-0737

## Summary
Severity: High
Advisory: CVE-2016-0737
Aliases: GHSA-972c-cfv8-2hq8, PYSEC-2026-929
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2016-0737
Type: osv

## Details
OpenStack Object Storage (Swift) before 2.4.0 does not properly close client connections, which allows remote attackers to cause a denial of service (proxy-server resource consumption) via a series of interrupted requests to a Large Object URL.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/81432
- https://review.openstack.org/#/c/217750/
- http://rhn.redhat.com/errata/RHSA-2016-0128.html
- http://rhn.redhat.com/errata/RHSA-2016-0155.html
- http://rhn.redhat.com/errata/RHSA-2016-0329.html
- https://bugs.launchpad.net/swift/+bug/1466549
- https://launchpad.net/swift/+milestone/2.4.0
- https://security.openstack.org/ossa/OSSA-2016-004.html
