# [M] CVE-2017-7200

## Summary
Severity: Medium
Advisory: CVE-2017-7200
Aliases: GHSA-j6mr-cm6x-h6jg, PYSEC-2026-814
CVSS: 5.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2017-03-21
Source: https://osv.dev/vulnerability/CVE-2017-7200
Type: osv

## Details
An SSRF issue was discovered in OpenStack Glance before Newton. The 'copy_from' feature in the Image Service API v1 allowed an attacker to perform masked network port scans. With v1, it is possible to create images with a URL such as 'http://localhost:22'. This could then allow an attacker to enumerate internal network details while appearing masked, since the scan would appear to originate from the Glance Image service.

## References
- http://www.securityfocus.com/bid/96988
- https://bugs.launchpad.net/ossn/+bug/1153614
- https://bugs.launchpad.net/ossn/+bug/1606495
- https://wiki.openstack.org/wiki/OSSN/OSSN-0078
