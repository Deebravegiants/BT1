# [H] CVE-2016-4383

## Summary
Severity: High
Advisory: CVE-2016-4383
CVSS: 8.4 (CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2017-06-27
Source: https://osv.dev/vulnerability/CVE-2016-4383
Type: osv

## Details
The glance-manage db in all versions of HPE Helion Openstack Glance allows deleted image ids to be reassigned, which allows remote authenticated users to cause other users to boot into a modified image without notification of the change.

## References
- http://www.securityfocus.com/bid/93106
- https://bugs.launchpad.net/glance/+bug/1593799/
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05273584
- https://wiki.openstack.org/wiki/OSSN/OSSN-0075
- https://wiki.openstack.org/wiki/OSSN/OSSN-0075
- https://bugs.launchpad.net/glance/+bug/1593799/
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05273584
