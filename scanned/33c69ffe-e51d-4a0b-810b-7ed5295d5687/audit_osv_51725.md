# [M] CVE-2021-38204

## Summary
Severity: Medium
Advisory: CVE-2021-38204
Aliases: A-196448784, ASB-A-196448784
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-08-08
Source: https://osv.dev/vulnerability/CVE-2021-38204
Type: osv

## Details
drivers/usb/host/max3421-hcd.c in the Linux kernel before 5.13.6 allows physically proximate attackers to cause a denial of service (use-after-free and panic) by removing a MAX-3421 USB device in certain situations.

## References
- https://lists.debian.org/debian-lts-announce/2021/12/msg00012.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.6
- https://github.com/torvalds/linux/commit/b5fdf5c6e6bee35837e160c00ac89327bdad031b
