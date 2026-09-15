# [M] usb: usbip: fix a refcount leak in stub_probe()

## Summary
Severity: Medium
Advisory: CVE-2022-49389
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49389
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: usbip: fix a refcount leak in stub_probe()

usb_get_dev() is called in stub_device_alloc(). When stub_probe() fails
after that, usb_put_dev() needs to be called to release the reference.

Fix this by moving usb_put_dev() to sdev_free error path handling.

Find this by code review.

## References
- https://git.kernel.org/stable/c/11c65408bd0ba1d9cd1307caa38169292de9cdfb
- https://git.kernel.org/stable/c/247d3809e45a34d9e1a3a2bb7012e31ed8b46031
- https://git.kernel.org/stable/c/2f0ae93ec33c8456cdfbf7876b80403a6318ebce
- https://git.kernel.org/stable/c/51422046be504515eb5a591adf0f424b62f46804
- https://git.kernel.org/stable/c/6bafee2f18af5e5ac125e42960bc65496d0e56a0
- https://git.kernel.org/stable/c/8afb048800919d0ab10c57983940eba956339f21
- https://git.kernel.org/stable/c/9ec4cbf1cc55d126759051acfe328d489c5d6e60
- https://git.kernel.org/stable/c/bcbb795a9e78180d74c6ab21518da87e803dfdce
- https://git.kernel.org/stable/c/f20d2d3b3364ce6525c050a8b6b4c54c8c19674d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49389.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
