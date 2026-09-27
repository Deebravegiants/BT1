# [H] CVE-2016-9602

## Summary
Severity: High
Advisory: CVE-2016-9602
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-26
Source: https://osv.dev/vulnerability/CVE-2016-9602
Type: osv

## Details
Qemu before version 2.9 is vulnerable to an improper link following when built with the VirtFS. A privileged user inside guest could use this flaw to access host file system beyond the shared folder and potentially escalating their privileges on a host.

## References
- http://www.openwall.com/lists/oss-security/2017/01/17/12
- http://www.securityfocus.com/bid/95461
- http://www.securitytracker.com/id/1037604
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://lists.gnu.org/archive/html/qemu-devel/2017-01/msg06225.html
- https://lists.gnu.org/archive/html/qemu-devel/2017-02/msg04347.html
- https://security.gentoo.org/glsa/201704-01
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-9602
