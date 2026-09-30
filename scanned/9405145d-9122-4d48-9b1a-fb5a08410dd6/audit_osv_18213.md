# [M] CVE-2020-25085

## Summary
Severity: Medium
Advisory: CVE-2020-25085
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-25085
Type: osv

## Details
QEMU 5.0.0 has a heap-based Buffer Overflow in flatview_read_continue in exec.c because hw/sd/sdhci.c mishandles a write operation in the SDHC_BLKSIZE case.

## References
- https://lists.debian.org/debian-lts-announce/2020/11/msg00047.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20201009-0005/
- http://www.openwall.com/lists/oss-security/2020/09/16/6
- http://www.openwall.com/lists/oss-security/2021/03/09/1
- https://bugs.launchpad.net/qemu/+bug/1892960
- https://lists.nongnu.org/archive/html/qemu-devel/2020-09/msg00733.html
