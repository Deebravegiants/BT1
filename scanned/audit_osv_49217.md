# [H] CVE-2018-6412

## Summary
Severity: High
Advisory: CVE-2018-6412
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-01-31
Source: https://osv.dev/vulnerability/CVE-2018-6412
Type: osv

## Details
In the function sbusfb_ioctl_helper() in drivers/video/fbdev/sbuslib.c in the Linux kernel through 4.15, an integer signedness error allows arbitrary information leakage for the FBIOPUTCMAP_SPARC and FBIOGETCMAP_SPARC commands.

## References
- https://github.com/torvalds/linux/commit/250c6c49e3b68756b14983c076183568636e2bde
- https://marc.info/?l=linux-fbdev&m=151734425901499&w=2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=250c6c49e3b68756b14983c076183568636e2bde
