# [M] CVE-2018-1130

## Summary
Severity: Medium
Advisory: CVE-2018-1130
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-1130
Type: osv

## Details
Linux kernel before version 4.16-rc7 is vulnerable to a null pointer dereference in dccp_write_xmit() function in net/dccp/output.c in that allows a local user to cause a denial of service by a number of certain crafted system calls.

## References
- https://usn.ubuntu.com/3654-1/
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://usn.ubuntu.com/3656-1/
- https://access.redhat.com/errata/RHSA-2018:1854
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3697-2/
- https://usn.ubuntu.com/3698-1/
- https://usn.ubuntu.com/3698-2/
- https://lists.debian.org/debian-lts-announce/2018/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://syzkaller.appspot.com/bug?id=833568de043e0909b2aeaef7be136db39d21ba94
- https://usn.ubuntu.com/3654-2/
- https://usn.ubuntu.com/3697-1/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1130
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=67f93df79aeefc3add4e4b31a752600f834236e2
- https://marc.info/?l=linux-netdev&m=152036596825220&w=2
