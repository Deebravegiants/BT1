# [M] CVE-2019-20636

## Summary
Severity: Medium
Advisory: CVE-2019-20636
Aliases: A-153715664, ASB-A-153715664
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-08
Source: https://osv.dev/vulnerability/CVE-2019-20636
Type: osv

## Details
In the Linux kernel before 5.4.12, drivers/input/input.c has out-of-bounds writes via a crafted keycode table, as demonstrated by input_set_keycode, aka CID-cb222aed03d7.

## References
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200430-0004/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.12
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cb222aed03d798fc074be55e59d9a112338ee784
- https://github.com/torvalds/linux/commit/cb222aed03d798fc074be55e59d9a112338ee784
