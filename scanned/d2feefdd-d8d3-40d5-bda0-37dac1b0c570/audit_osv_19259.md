# [H] CVE-2020-9383

## Summary
Severity: High
Advisory: CVE-2020-9383
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-02-25
Source: https://osv.dev/vulnerability/CVE-2020-9383
Type: osv

## Details
An issue was discovered in the Linux kernel 3.16 through 5.5.6. set_fdc in drivers/block/floppy.c leads to a wait_til_ready out-of-bounds read because the FDC index is not checked for errors before assigning it, aka CID-2e90ca68b0d2.

## References
- https://usn.ubuntu.com/4345-1/
- https://usn.ubuntu.com/4346-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00039.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200313-0003/
- https://www.debian.org/security/2020/dsa-4698
- https://usn.ubuntu.com/4342-1/
- https://usn.ubuntu.com/4344-1/
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=2f9ac30a54dc0181ddac3705cdcf4775d863c530
- https://github.com/torvalds/linux/commit/2e90ca68b0d2f5548804f22f0dd61145516171e3
