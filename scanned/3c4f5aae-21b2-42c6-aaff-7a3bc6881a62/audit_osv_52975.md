# [M] CVE-2022-2380

## Summary
Severity: Medium
Advisory: CVE-2022-2380
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-13
Source: https://osv.dev/vulnerability/CVE-2022-2380
Type: osv

## Details
The Linux kernel was found vulnerable out of bounds memory access in the drivers/video/fbdev/sm712fb.c:smtcfb_read() function. The vulnerability could result in local attackers being able to crash the kernel.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/deller/linux-fbdev.git/commit/?h=for-next&id=bd771cf5c4254511cc4abb88f3dab3bd58bdf8e8
