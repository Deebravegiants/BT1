# [H] CVE-2018-1069

## Summary
Severity: High
Advisory: CVE-2018-1069
CVSS: 7.1 (CVSS:3.0/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-1069
Type: osv

## Details
Red Hat OpenShift Enterprise version 3.7 is vulnerable to access control override for container network filesystems. An attacker could override the UserId and GroupId for GlusterFS and NFS to read and write any data on the network filesystem.

## References
- http://www.securityfocus.com/bid/103364
- https://bugzilla.redhat.com/show_bug.cgi?id=1552987
