# [H] HID: core: do not bypass hid_hw_raw_request

## Summary
Severity: High
Advisory: CVE-2025-38494
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38494
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: core: do not bypass hid_hw_raw_request

hid_hw_raw_request() is actually useful to ensure the provided buffer
and length are valid. Directly calling in the low level transport driver
function bypassed those checks and allowed invalid paramto be used.

## References
- https://git.kernel.org/stable/c/0e5017d84d650ca0eeaf4a3fe9264c5dbc886b81
- https://git.kernel.org/stable/c/19d1314d46c0d8a5c08ab53ddeb62280c77698c0
- https://git.kernel.org/stable/c/40e25aa7e4e0f2440c73a683ee448e41c7c344ed
- https://git.kernel.org/stable/c/a62a895edb2bfebffa865b5129a66e3b4287f34f
- https://git.kernel.org/stable/c/c2ca42f190b6714d6c481dfd3d9b62ea091c946b
- https://git.kernel.org/stable/c/d18f63e848840100dbc351a82e7042eac5a28cf5
- https://git.kernel.org/stable/c/dd8e8314f2ce225dade5248dcfb9e2ac0edda624
- https://git.kernel.org/stable/c/f10923b8d32a473b229477b63f23bbd72b1e9910
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38494.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38494
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
