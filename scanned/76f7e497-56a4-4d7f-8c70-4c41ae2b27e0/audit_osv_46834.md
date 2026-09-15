# [H] CVE-2015-5261

## Summary
Severity: High
Advisory: CVE-2015-5261
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2016-06-07
Source: https://osv.dev/vulnerability/CVE-2015-5261
Type: osv

## Details
Heap-based buffer overflow in SPICE before 0.12.6 allows guest OS users to read and write to arbitrary memory locations on the host via guest QXL commands related to surface creation.

## References
- http://rhn.redhat.com/errata/RHSA-2015-1889.html
- http://rhn.redhat.com/errata/RHSA-2015-1890.html
- http://www.debian.org/security/2015/dsa-3371
- http://www.ubuntu.com/usn/USN-2766-1
- https://security.gentoo.org/glsa/201606-05
- https://bugzilla.redhat.com/show_bug.cgi?id=1261889
- http://lists.freedesktop.org/archives/spice-devel/2015-October/022191.html
- http://www.openwall.com/lists/oss-security/2015/10/06/4
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securitytracker.com/id/1033753
