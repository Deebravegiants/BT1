# [H] CVE-2022-45885

## Summary
Severity: High
Advisory: CVE-2022-45885
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-45885
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.9. drivers/media/dvb-core/dvb_frontend.c has a race condition that can cause a use-after-free when a device is disconnected.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6769a0b7ee0c3b31e1b22c3fadff2bfb642de23f
- https://lore.kernel.org/linux-media/20221115131822.6640-1-imv4bel%40gmail.com/
- https://lore.kernel.org/linux-media/20221115131822.6640-2-imv4bel%40gmail.com/
- https://security.netapp.com/advisory/ntap-20230113-0006/
