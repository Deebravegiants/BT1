# [H] ALSA: pcm: Don't setup bogus iov_iter for silencing

## Summary
Severity: High
Advisory: CVE-2026-64134
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64134
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Don't setup bogus iov_iter for silencing

At transition to the iov_iter for PCM data transfer, we blindly
applied the iov_iter setup also for silencing (i.e. data = NULL), and
it leads to a calculation of bogus iov_iter.  Fortunately this didn't
cause troubles on most of architectures but it goes wrong on RISC-V
now, causing a NULL dereference.

Handle the NULL data case to treat the silencing in interleaved_copy()
for addressing the bug above.  noninterleaved_copy() has already the
NULL data handling, so it doesn't need changes.

## References
- https://git.kernel.org/stable/c/41a766c647294842c9b17672449f8e011048cba9
- https://git.kernel.org/stable/c/c9f6768515818d71bdfc20119a81f3332c53b9c6
- https://git.kernel.org/stable/c/ce836587e594af39ff048d9b29dee0f5f10692c9
- https://git.kernel.org/stable/c/e4d3386b74fba8e01280484b67ee481ece00201e
- https://git.kernel.org/stable/c/feff0251386aa6bb180a0a1cf7c1f91ba868113d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64134.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
