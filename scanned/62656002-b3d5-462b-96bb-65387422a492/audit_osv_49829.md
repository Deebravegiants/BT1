# [M] CVE-2019-19532

## Summary
Severity: Medium
Advisory: CVE-2019-19532
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-19532
Type: osv

## Details
In the Linux kernel before 5.3.9, there are multiple out-of-bounds write bugs that can be caused by a malicious USB device in the Linux kernel HID drivers, aka CID-d9d4b1e46d95. This affects drivers/hid/hid-axff.c, drivers/hid/hid-dr.c, drivers/hid/hid-emsff.c, drivers/hid/hid-gaff.c, drivers/hid/hid-holtekff.c, drivers/hid/hid-lg2ff.c, drivers/hid/hid-lg3ff.c, drivers/hid/hid-lg4ff.c, drivers/hid/hid-lgff.c, drivers/hid/hid-logitech-hidpp.c, drivers/hid/hid-microsoft.c, drivers/hid/hid-sony.c, drivers/hid/hid-tmff.c, and drivers/hid/hid-zpff.c.

## References
- https://usn.ubuntu.com/4226-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- http://www.openwall.com/lists/oss-security/2019/12/03/4
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d9d4b1e46d9543a82c23f6df03f4ad697dab361b
