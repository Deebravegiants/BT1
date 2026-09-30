# [H] CVE-2022-45884

## Summary
Severity: High
Advisory: CVE-2022-45884
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-45884
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.9. drivers/media/dvb-core/dvbdev.c has a use-after-free, related to dvb_register_device dynamically allocating fops.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=627bb528b086b4136315c25d6a447a98ea9448d3
- https://lore.kernel.org/linux-media/20221115131822.6640-1-imv4bel%40gmail.com/
- https://lore.kernel.org/linux-media/20221115131822.6640-4-imv4bel%40gmail.com/
- https://security.netapp.com/advisory/ntap-20230113-0006/
