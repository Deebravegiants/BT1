# [H] HID: wacom: fix out-of-bounds read in wacom_intuos_bt_irq

## Summary
Severity: High
Advisory: CVE-2026-43051
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43051
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: wacom: fix out-of-bounds read in wacom_intuos_bt_irq

The wacom_intuos_bt_irq() function processes Bluetooth HID reports
without sufficient bounds checking. A maliciously crafted short report
can trigger an out-of-bounds read when copying data into the wacom
structure.

Specifically, report 0x03 requires at least 22 bytes to safely read
the processed data and battery status, while report 0x04 (which
falls through to 0x03) requires 32 bytes.

Add explicit length checks for these report IDs and log a warning if
a short report is received.

## References
- https://git.kernel.org/stable/c/2f1763f62909ccb6386ac50350fa0abbf5bb16a9
- https://git.kernel.org/stable/c/3d78386b144453c47e81bf62dc3601b757f02d99
- https://git.kernel.org/stable/c/41026bcc0fdf82605205c27935ef719cbc07193b
- https://git.kernel.org/stable/c/5b5b9730111808410e404ceac2fabd32eef92fbd
- https://git.kernel.org/stable/c/8bd690ac1242332c73cba10dacdad6c6642bbb94
- https://git.kernel.org/stable/c/c8dc23c97680eebefde06da5858aaef1b37cf75d
- https://git.kernel.org/stable/c/d0ae84b3c9f3ea1a564eb1b7612113ca9fe8aada
- https://git.kernel.org/stable/c/fa8901cb1f0b2113a342db93bd5684b59fe99dcf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43051.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43051
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
