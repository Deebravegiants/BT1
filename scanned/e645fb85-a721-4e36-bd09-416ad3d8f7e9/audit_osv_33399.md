# [H] drm/vmwgfx: Validate command header size against SVGA_CMD_MAX_DATASIZE

## Summary
Severity: High
Advisory: CVE-2025-40277
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40277
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.59, >=6.13.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Validate command header size against SVGA_CMD_MAX_DATASIZE

This data originates from userspace and is used in buffer offset
calculations which could potentially overflow causing an out-of-bounds
access.

## References
- https://git.kernel.org/stable/c/32b415a9dc2c212e809b7ebc2b14bc3fbda2b9af
- https://git.kernel.org/stable/c/54d458b244893e47bda52ec3943fdfbc8d7d068b
- https://git.kernel.org/stable/c/5aea2cde03d4247cdcf53f9ab7d0747c9dca1cfc
- https://git.kernel.org/stable/c/709e5c088f9c99a5cf2c1d1c6ce58f2cca7ab173
- https://git.kernel.org/stable/c/a3abb54c27b2c393c44362399777ad2f6e1ff17e
- https://git.kernel.org/stable/c/b5df9e06eed3df6a4f5c6f8453013b0cabb927b4
- https://git.kernel.org/stable/c/e58559845021c3bad5e094219378b869157fad53
- https://git.kernel.org/stable/c/f3f3a8eb3f0ba799fae057091d8c67cca12d6fa0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40277.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
