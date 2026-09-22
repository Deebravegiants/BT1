# [M] CVE-2021-26931

## Summary
Severity: Medium
Advisory: CVE-2021-26931
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-17
Source: https://osv.dev/vulnerability/CVE-2021-26931
Type: osv

## Details
An issue was discovered in the Linux kernel 2.6.39 through 5.10.16, as used in Xen. Block, net, and SCSI backends consider certain errors a plain bug, deliberately causing a kernel crash. For errors potentially being at least under the influence of guests (such as out of memory conditions), it isn't correct to assume a plain bug. Memory allocations potentially causing such crashes occur only when Linux is running in PV mode, though. This affects drivers/block/xen-blkback/blkback.c and drivers/xen/xen-scsiback.c.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3194a1746e8aabe86075fd3c5e7cf1f4632d7f16
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5a264285ed1cd32e26d9de4f3c8c6855e467fd63
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7c77474b2d22176d2bfb592ec74e0f2cb71352c9
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2XQR52ICKRK3GC4HDWLMWF2U55YGAR63/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GWQWPWYZRXVFJI5M3VCM72X27IB7CKOB/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20210326-0001/
- http://xenbits.xen.org/xsa/advisory-362.html
