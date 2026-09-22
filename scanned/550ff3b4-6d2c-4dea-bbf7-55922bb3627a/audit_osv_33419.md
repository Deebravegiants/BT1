# [H] fbdev: bitblit: bound-check glyph index in bit_putcs*

## Summary
Severity: High
Advisory: CVE-2025-40322
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40322
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: bitblit: bound-check glyph index in bit_putcs*

bit_putcs_aligned()/unaligned() derived the glyph pointer from the
character value masked by 0xff/0x1ff, which may exceed the actual font's
glyph count and read past the end of the built-in font array.
Clamp the index to the actual glyph count before computing the address.

This fixes a global out-of-bounds read reported by syzbot.

## References
- https://git.kernel.org/stable/c/0998a6cb232674408a03e8561dc15aa266b2f53b
- https://git.kernel.org/stable/c/18c4ef4e765a798b47980555ed665d78b71aeadf
- https://git.kernel.org/stable/c/901f44227072be60812fe8083e83e1533c04eed1
- https://git.kernel.org/stable/c/9ba1a7802ca9a2590cef95b253e6526f4364477f
- https://git.kernel.org/stable/c/a10cede006f9614b465cf25609a8753efbfd45cc
- https://git.kernel.org/stable/c/c12003bf91fdff381c55ef54fef3e961a5af2545
- https://git.kernel.org/stable/c/db5c9a162d2f42bcc842b76b3d935dcc050a0eec
- https://git.kernel.org/stable/c/efaf89a75a29b2d179bf4fe63ca62852e93ad620
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40322.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40322
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
