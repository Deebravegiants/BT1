# [H] CVE-2018-11506

## Summary
Severity: High
Advisory: CVE-2018-11506
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-28
Source: https://osv.dev/vulnerability/CVE-2018-11506
Type: osv

## Details
The sr_do_ioctl function in drivers/scsi/sr_ioctl.c in the Linux kernel through 4.16.12 allows local users to cause a denial of service (stack-based buffer overflow) or possibly have unspecified other impact because sense buffers have different sizes at the CDROM layer and the SCSI layer, as demonstrated by a CDROMREADMODE2 ioctl call.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://twitter.com/efrmv/status/1001574894273007616
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://github.com/torvalds/linux/commit/f7068114d45ec55996b9040e98111afa56e010fe
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f7068114d45ec55996b9040e98111afa56e010fe
