# [M] CVE-2018-10940

## Summary
Severity: Medium
Advisory: CVE-2018-10940
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-09
Source: https://osv.dev/vulnerability/CVE-2018-10940
Type: osv

## Details
The cdrom_ioctl_media_changed function in drivers/cdrom/cdrom.c in the Linux kernel before 4.16.6 allows local attackers to use a incorrect bounds check in the CDROM driver CDROM_MEDIA_CHANGED ioctl to read out kernel memory.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://usn.ubuntu.com/3695-1/
- https://usn.ubuntu.com/3754-1/
- https://usn.ubuntu.com/3695-2/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3096
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.6
- https://access.redhat.com/errata/RHSA-2018:3083
- https://lists.debian.org/debian-lts-announce/2018/06/msg00000.html
- https://usn.ubuntu.com/3676-2/
- https://usn.ubuntu.com/3676-1/
- http://www.securityfocus.com/bid/104154
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9de4ee40547fd315d4a0ed1dd15a2fa3559ad707
- https://github.com/torvalds/linux/commit/9de4ee40547fd315d4a0ed1dd15a2fa3559ad707
