# [H] CVE-2023-35828

## Summary
Severity: High
Advisory: CVE-2023-35828
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-18
Source: https://osv.dev/vulnerability/CVE-2023-35828
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.3.2. A use-after-free was found in renesas_usb3_remove in drivers/usb/gadget/udc/renesas_usb3.c.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=2b947f8769be8b8181dc795fd292d3e7120f5204
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://lore.kernel.org/all/20230327121700.52d881e0%40canb.auug.org.au/
- https://security.netapp.com/advisory/ntap-20230803-0002/
- https://lore.kernel.org/lkml/CAJedcCwkuznS1kSTvJXhzPoavcZDWNhNMshi-Ux0spSVRwU=RA%40mail.gmail.com/T/
