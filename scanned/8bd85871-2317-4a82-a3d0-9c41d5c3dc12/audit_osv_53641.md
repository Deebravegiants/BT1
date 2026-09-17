# [M] CVE-2023-1079

## Summary
Severity: Medium
Advisory: CVE-2023-1079
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-1079
Type: osv

## Details
A flaw was found in the Linux kernel. A use-after-free may be triggered in asus_kbd_backlight_set when plugging/disconnecting in a malicious USB device, which advertises itself as an Asus device. Similarly to the previous known CVE-2023-25012, but in asus devices, the work_struct may be scheduled by the LED controller while the device is disconnecting, triggering a use-after-free on the struct asus_kbd_leds *led structure. A malicious USB device may exploit the issue to cause memory corruption with controlled data.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://git.kernel.org/pub/scm/linux/kernel/git/next/linux-next.git/commit/?id=4ab3a086d10eeec1424f2e8a968827a6336203df
