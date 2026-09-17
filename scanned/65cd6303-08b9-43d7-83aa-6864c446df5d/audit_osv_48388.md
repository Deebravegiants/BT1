# [H] CVE-2017-7187

## Summary
Severity: High
Advisory: CVE-2017-7187
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-7187
Type: osv

## Details
The sg_ioctl function in drivers/scsi/sg.c in the Linux kernel through 4.10.4 allows local users to cause a denial of service (stack-based buffer overflow) or possibly have unspecified other impact via a large command size in an SG_NEXT_CMD_LEN ioctl call, leading to out-of-bounds write access in the sg_write function.

## References
- https://source.android.com/security/bulletin/pixel/2017-10-01
- http://www.securityfocus.com/bid/96989
- http://www.securitytracker.com/id/1038086
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://access.redhat.com/errata/RHSA-2017:2669
- https://gist.github.com/dvyukov/48ad14e84de45b0be92b7f0eda20ff1b
- https://git.kernel.org/pub/scm/linux/kernel/git/mkp/scsi.git/commit/?h=4.11/scsi-fixes&id=bf33f87dd04c371ea33feb821b60d63d754e3124
