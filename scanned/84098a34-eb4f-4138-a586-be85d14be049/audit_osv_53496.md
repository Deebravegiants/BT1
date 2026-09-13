# [M] CVE-2022-45887

## Summary
Severity: Medium
Advisory: CVE-2022-45887
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-45887
Type: osv

## Details
An issue was discovered in the Linux kernel through 6.0.9. drivers/media/usb/ttusb-dec/ttusb_dec.c has a memory leak because of the lack of a dvb_frontend_detach call.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=517a281338322ff8293f988771c98aaa7205e457
- https://lore.kernel.org/linux-media/20221115131822.6640-1-imv4bel%40gmail.com/
- https://lore.kernel.org/linux-media/20221115131822.6640-5-imv4bel%40gmail.com/
- https://security.netapp.com/advisory/ntap-20230113-0006/
