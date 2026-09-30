# [M] CVE-2019-15090

## Summary
Severity: Medium
Advisory: CVE-2019-15090
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-16
Source: https://osv.dev/vulnerability/CVE-2019-15090
Type: osv

## Details
An issue was discovered in drivers/scsi/qedi/qedi_dbg.c in the Linux kernel before 5.1.12. In the qedi_dbg_* family of functions, there is an out-of-bounds read.

## References
- https://usn.ubuntu.com/4147-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://usn.ubuntu.com/4118-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.12
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://usn.ubuntu.com/4115-1/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c09581a52765a85f19fc35340127396d5e3379cc
- https://github.com/torvalds/linux/commit/c09581a52765a85f19fc35340127396d5e3379cc
