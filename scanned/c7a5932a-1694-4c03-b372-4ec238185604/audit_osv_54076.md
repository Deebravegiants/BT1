# [M] CVE-2023-38409

## Summary
Severity: Medium
Advisory: CVE-2023-38409
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-17
Source: https://osv.dev/vulnerability/CVE-2023-38409
Type: osv

## Details
An issue was discovered in set_con2fb_map in drivers/video/fbdev/core/fbcon.c in the Linux kernel before 6.2.12. Because an assignment occurs only for the first vc, the fbcon_registered_fb and fbcon_display arrays can be desynchronized in fbcon_mode_deleted (the con2fb_map points at the old fb_info).

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.12
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=fffb0b52d5258554c645c966c6cbef7de50b851d
