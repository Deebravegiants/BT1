# [H] Bluetooth: btrtl: validate firmware patch bounds

## Summary
Severity: High
Advisory: CVE-2026-68479
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68479
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: btrtl: validate firmware patch bounds

rtlbt_parse_firmware() copies patch_length - 4 bytes before appending the
firmware version. A malformed firmware patch shorter than the version field
can make this subtraction underflow and turn the copy into an oversized
read and write during Bluetooth setup.

The existing patch_offset + patch_length check can also wrap on 32-bit
architectures. Validate the patch length and range without arithmetic
overflow before allocating or copying the patch.

## References
- https://git.kernel.org/stable/c/39e01b4addfbbe177567d6ed1dfb81f9cccb19e6
- https://git.kernel.org/stable/c/609c5b04a28dc1b0f3af6a7bc93055135b2d2059
- https://git.kernel.org/stable/c/6744ab60dfac55d1df5733960aad5be300984301
- https://git.kernel.org/stable/c/68c5a2a19987c035eb129e627e579adafb04f637
- https://git.kernel.org/stable/c/83534891c058ed71e251135072640911670869aa
- https://git.kernel.org/stable/c/a4cb830e0b55ac76c849fd7840afb251f4c028fa
- https://git.kernel.org/stable/c/bda3c598ade6ea03884074b91e31608326684921
- https://git.kernel.org/stable/c/f1ca750c0510bdbb504bf084d2f196ef2af92ea6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68479.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68479
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
