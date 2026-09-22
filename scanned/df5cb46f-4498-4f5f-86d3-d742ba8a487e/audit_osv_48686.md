# [M] CVE-2018-1118

## Summary
Severity: Medium
Advisory: CVE-2018-1118
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-1118
Type: osv

## Details
Linux kernel vhost since version 4.8 does not properly initialize memory in messages passed between virtual guests and the host operating system in the vhost/vhost.c:vhost_new_msg() function. This can allow local privileged users to read some kernel memory contents when reading from the /dev/vhost-net device file.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3762-1/
- https://usn.ubuntu.com/3762-2/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1118
