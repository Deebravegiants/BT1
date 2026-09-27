# [H] speakup: Fix sizeof() vs ARRAY_SIZE() bug

## Summary
Severity: High
Advisory: CVE-2024-38587
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38587
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

speakup: Fix sizeof() vs ARRAY_SIZE() bug

The "buf" pointer is an array of u16 values.  This code should be
using ARRAY_SIZE() (which is 256) instead of sizeof() (which is 512),
otherwise it can the still got out of bounds.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/008ab3c53bc4f0b2f20013c8f6c204a3203d0b8b
- https://git.kernel.org/stable/c/07ef95cc7a579731198c93beed281e3a79a0e586
- https://git.kernel.org/stable/c/3726f75a1ccc16cd335c0ccfad1d92ee08ecba5e
- https://git.kernel.org/stable/c/42f0a3f67158ed6b2908d2b9ffbf7e96d23fd358
- https://git.kernel.org/stable/c/504178fb7d9f6cdb0496d5491efb05f45597e535
- https://git.kernel.org/stable/c/c6e1650cf5df1bd6638eeee231a683ef30c7d4eb
- https://git.kernel.org/stable/c/cd7f3978c2ec741aedd1d860b2adb227314cf996
- https://git.kernel.org/stable/c/d52c04474feac8e305814a5228e622afe481b2ef
- https://git.kernel.org/stable/c/eb1ea64328d4cc7d7a912c563f8523d5259716ef
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38587.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38587
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
