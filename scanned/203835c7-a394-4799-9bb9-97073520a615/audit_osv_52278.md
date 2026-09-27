# [M] CVE-2021-47273

## Summary
Severity: Medium
Advisory: CVE-2021-47273
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47273
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: dwc3-meson-g12a: fix usb2 PHY glue init when phy0 is disabled

When only PHY1 is used (for example on Odroid-HC4), the regmap init code
uses the usb2 ports when doesn't initialize the PHY1 regmap entry.

This fixes:
Unable to handle kernel NULL pointer dereference at virtual address 0000000000000020
...
pc : regmap_update_bits_base+0x40/0xa0
lr : dwc3_meson_g12a_usb2_init_phy+0x4c/0xf8
...
Call trace:
regmap_update_bits_base+0x40/0xa0
dwc3_meson_g12a_usb2_init_phy+0x4c/0xf8
dwc3_meson_g12a_usb2_init+0x7c/0xc8
dwc3_meson_g12a_usb_init+0x28/0x48
dwc3_meson_g12a_probe+0x298/0x540
platform_probe+0x70/0xe0
really_probe+0xf0/0x4d8
driver_probe_device+0xfc/0x168
...

## References
- https://git.kernel.org/stable/c/4d2aa178d2ad2fb156711113790dde13e9aa2376
- https://git.kernel.org/stable/c/750a0d75564293be3ed50f13ef7f38ab75106421
- https://git.kernel.org/stable/c/d8dd3754e707104a34f8ec595034d503ea8871a2
