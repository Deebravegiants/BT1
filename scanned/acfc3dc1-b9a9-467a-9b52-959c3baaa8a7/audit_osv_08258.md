# [H] CVE-2016-20022

## Summary
Severity: High
Advisory: CVE-2016-20022
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-27
Source: https://osv.dev/vulnerability/CVE-2016-20022
Type: osv

## Details
In the Linux kernel before 4.8, usb_parse_endpoint in drivers/usb/core/config.c does not validate the wMaxPacketSize field of an endpoint descriptor. NOTE: This vulnerability only affects products that are no longer supported by the supplier.

## References
- https://lore.kernel.org/lkml/1486322541-8206-8-git-send-email-w%401wt.eu/
- https://www.spinics.net/lists/linux-usb/msg144177.html
- https://github.com/torvalds/linux/commit/aed9d65ac3278d4febd8665bd7db59ef53e825fe
