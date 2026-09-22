# [H] crypto: ecc - Fix carry overflow in vli multiplication

## Summary
Severity: High
Advisory: CVE-2026-64313
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64313
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: ecc - Fix carry overflow in vli multiplication

The carry flag calculation fails when r01.m_high is saturated
(0xFFFFFFFFFFFFFFFF) and addition of lower bits overflows.

The condition (r01.m_high < product.m_high) doesn't handle the case
where r01.m_high == product.m_high and an additional carry exists
from lower-bit overflow.

When commit 3c4b23901a0c ("crypto: ecdh - Add ECDH software support")
introduced crypto/ecc.c, it split the muladd() function in the
micro-ecc library into separate mul_64_64() and add_128_128() helpers.
It seems the check got lost in translation.

Add proper handling for this boundary by accounting for the carry
from the lower addition.

## References
- https://git.kernel.org/stable/c/24a54dfa06d09813b4802a374fad3d2c0e16a884
- https://git.kernel.org/stable/c/27b536a2ec8e2f85a0380c2d13c9ecbc7aaab406
- https://git.kernel.org/stable/c/5275e0fca256d081e2e7d4ba3dd8216c6e50d44e
- https://git.kernel.org/stable/c/677450e5ef850c4d28b7956aa01104548c2a894e
- https://git.kernel.org/stable/c/774ddddf5eb26eeca177350413e3e2bc50930ee9
- https://git.kernel.org/stable/c/b709e0e768766abe29a49e1c1922a1604be602f4
- https://git.kernel.org/stable/c/d11b2bb99bec1f5557c01cac42231e23745f49b8
- https://git.kernel.org/stable/c/ebaae7c4251cc0cdb2602f334d4f08a3e82d271e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64313.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
