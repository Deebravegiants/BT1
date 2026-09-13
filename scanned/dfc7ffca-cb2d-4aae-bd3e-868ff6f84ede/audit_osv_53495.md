# [H] CVE-2022-45886

## Summary
Severity: High
Advisory: CVE-2022-45886
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-45886
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.9. drivers/media/dvb-core/dvb_net.c has a .disconnect versus dvb_device_open race condition that leads to a use-after-free.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4172385b0c9ac366dcab78eda48c26814b87ed1a
- https://security.netapp.com/advisory/ntap-20230113-0006/
- https://lore.kernel.org/linux-media/20221115131822.6640-1-imv4bel%40gmail.com/
- https://lore.kernel.org/linux-media/20221115131822.6640-3-imv4bel%40gmail.com/
