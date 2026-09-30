# [M] CVE-2017-2618

## Summary
Severity: Medium
Advisory: CVE-2017-2618
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-2618
Type: osv

## Details
A flaw was found in the Linux kernel's handling of clearing SELinux attributes on /proc/pid/attr files before 4.9.10. An empty (null) write to this file can crash the system by causing the system to attempt to access unmapped kernel memory.

## References
- https://access.redhat.com/errata/RHSA-2017:0931
- https://access.redhat.com/errata/RHSA-2017:0932
- https://access.redhat.com/errata/RHSA-2017:0933
- https://www.debian.org/security/2017/dsa-3791
- http://www.securityfocus.com/bid/96272
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2618
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=0c461cb727d146c9ef2d3e86214f498b78b7d125
- https://marc.info/?l=selinux&m=148588165923772&w=2
