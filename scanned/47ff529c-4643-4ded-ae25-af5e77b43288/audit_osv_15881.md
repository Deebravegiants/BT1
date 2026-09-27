# [H] CVE-2019-20175

## Summary
Severity: High
Advisory: CVE-2019-20175
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-12-31
Source: https://osv.dev/vulnerability/CVE-2019-20175
Type: osv

## Details
An issue was discovered in ide_dma_cb() in hw/ide/core.c in QEMU 2.4.0 through 4.2.0. The guest system can crash the QEMU process in the host system via a special SCSI_IOCTL_SEND_COMMAND. It hits an assertion that implies that the size of successful DMA transfers there must be a multiple of 512 (the size of a sector). NOTE: a member of the QEMU security team disputes the significance of this issue because a "privileged guest user has many ways to cause similar DoS effect, without triggering this assert.

## References
- https://www.mail-archive.com/qemu-devel%40nongnu.org/msg667396.html
- https://lists.nongnu.org/archive/html/qemu-devel/2019-07/msg03869.html
- https://lists.nongnu.org/archive/html/qemu-devel/2019-11/msg00597.html
- https://lists.nongnu.org/archive/html/qemu-devel/2019-11/msg02165.html
- https://lists.nongnu.org/archive/html/qemu-devel/2019-07/msg01651.html
