# [M] CVE-2016-2391

## Summary
Severity: Medium
Advisory: CVE-2016-2391
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-2391
Type: osv

## Details
The ohci_bus_start function in the USB OHCI emulation support (hw/usb/hcd-ohci.c) in QEMU allows local guest OS administrators to cause a denial of service (NULL pointer dereference and QEMU process crash) via vectors related to multiple eof_timers.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=fa1298c2d623522eda7b4f1f721fcb935abb7360
- http://www.openwall.com/lists/oss-security/2016/02/16/2
- http://www.securityfocus.com/bid/83263
- http://www.ubuntu.com/usn/USN-2974-1
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1304794
- https://lists.gnu.org/archive/html/qemu-devel/2016-02/msg03374.html
