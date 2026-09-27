# [H] HID: cp2112: prevent a buffer overflow in cp2112_xfer()

## Summary
Severity: High
Advisory: CVE-2022-50156
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50156
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: cp2112: prevent a buffer overflow in cp2112_xfer()

Smatch warnings:
drivers/hid/hid-cp2112.c:793 cp2112_xfer() error: __memcpy()
'data->block[1]' too small (33 vs 255)
drivers/hid/hid-cp2112.c:793 cp2112_xfer() error: __memcpy() 'buf' too
small (64 vs 255)

The 'read_length' variable is provided by 'data->block[0]' which comes
from user and it(read_length) can take a value between 0-255. Add an
upper bound to 'read_length' variable to prevent a buffer overflow in
memcpy().

## References
- https://git.kernel.org/stable/c/26e427ac85c2b8d0d108cc80b6de34d33e2780c4
- https://git.kernel.org/stable/c/381583845d19cb4bd21c8193449385f3fefa9caf
- https://git.kernel.org/stable/c/3af7d60e9a6c17d6d41c4341f8020511887d372d
- https://git.kernel.org/stable/c/519ff31a6ddd87aa4905bd9bf3b92e8b88801614
- https://git.kernel.org/stable/c/8489a20ac481b08c0391608d81ed3796d373cfdf
- https://git.kernel.org/stable/c/e7028944e61014ae915e7fb74963d3835f2f761a
- https://git.kernel.org/stable/c/ebda3d6b004bb6127a66a616524a2de152302ca7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50156.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50156
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
