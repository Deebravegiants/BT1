# [H] crypto: qat - validate RSA CRT component lengths

## Summary
Severity: High
Advisory: CVE-2026-64304
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64304
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: qat - validate RSA CRT component lengths

The generic RSA key parser (rsa_helper.c) bounds each CRT component (p,
q, dp, dq, qinv) by the modulus size n_sz, but qat_rsa_setkey_crt()
allocates half-size DMA buffers (key_sz / 2) and right-aligns each
component with:

    memcpy(dst + half_key_sz - len, src, len)

When a CRT component is larger than half_key_sz the subtraction
underflows and memcpy writes past the DMA buffer, causing memory
corruption.

Add a len > half_key_sz check next to the existing !len check for each
of the five CRT components so the driver falls back to the non-CRT path
instead of writing out of bounds.

## References
- https://git.kernel.org/stable/c/1002719d13072a5e4be1e993aa61dffb4a604e82
- https://git.kernel.org/stable/c/3d61a214fdcda41f1ebfabbb483404032a7b4d91
- https://git.kernel.org/stable/c/500319830d76911c120dc0b9605f8c16d7702844
- https://git.kernel.org/stable/c/6d99c5fadd2df488103f64d6475b63ba6852202b
- https://git.kernel.org/stable/c/6fb62b767f3e27661e8f8d2f7b85f4e098fcdb1a
- https://git.kernel.org/stable/c/b3ac78756588059729b9195fcc9f4b37d54057a5
- https://git.kernel.org/stable/c/c34369473bfe92a0b46ec78d6358e30341c7f481
- https://git.kernel.org/stable/c/ce42224487c504aee4b7ff3a7342e7b4d7e28cc9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64304.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
