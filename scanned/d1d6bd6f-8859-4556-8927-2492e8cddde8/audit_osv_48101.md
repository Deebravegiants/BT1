# [M] CVE-2017-18203

## Summary
Severity: Medium
Advisory: CVE-2017-18203
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-27
Source: https://osv.dev/vulnerability/CVE-2017-18203
Type: osv

## Details
The dm_get_from_kobject function in drivers/md/dm.c in the Linux kernel before 4.14.3 allow local users to cause a denial of service (BUG) by leveraging a race condition with __dm_destroy during creation and removal of DM devices.

## References
- https://usn.ubuntu.com/3655-2/
- https://usn.ubuntu.com/3657-1/
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3653-1/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3653-2/
- https://usn.ubuntu.com/3655-1/
- https://usn.ubuntu.com/3619-1/
- http://www.securityfocus.com/bid/103184
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://www.debian.org/security/2018/dsa-4187
- https://access.redhat.com/errata/RHSA-2018:1854
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.3
- https://access.redhat.com/errata/RHSA-2019:4154
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b9a41d21dceadf8104812626ef85dc56ee8a60ed
- https://github.com/torvalds/linux/commit/b9a41d21dceadf8104812626ef85dc56ee8a60ed
