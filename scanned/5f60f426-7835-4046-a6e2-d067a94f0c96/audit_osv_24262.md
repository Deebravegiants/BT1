# [H] erofs: validate the extent length for uncompressed pclusters

## Summary
Severity: High
Advisory: CVE-2022-50746
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50746
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

erofs: validate the extent length for uncompressed pclusters

syzkaller reported a KASAN use-after-free:
https://syzkaller.appspot.com/bug?extid=2ae90e873e97f1faf6f2

The referenced fuzzed image actually has two issues:
 - m_pa == 0 as a non-inlined pcluster;
 - The logical length is longer than its physical length.

The first issue has already been addressed.  This patch addresses
the second issue by checking the extent length validity.

## References
- https://git.kernel.org/stable/c/40c73b2ea9611b5388807be406f30f5e4e1162da
- https://git.kernel.org/stable/c/c505feba4c0d76084e56ec498ce819f02a7043ae
- https://git.kernel.org/stable/c/dc8b6bd587b13b85aff6e9d36cdfcd3f955cac9e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50746.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50746
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
