# [H] xsk: require at least 16 bytes of TX metadata

## Summary
Severity: High
Advisory: CVE-2026-74710
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74710
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: require at least 16 bytes of TX metadata

AF_XDP accepts a TX metadata length as small as eight bytes, but every
supported request needs the flags plus at least one eight-byte request
field. Such short metadata also lets the kernel read beyond the registered
area.

Require 16 bytes rather than sizeof(struct xsk_tx_metadata) to preserve
compatibility with applications that do not use launch-time metadata.

## References
- https://git.kernel.org/stable/c/1bb30b181d9f0484e141f8411e15ed906d5c6780
- https://git.kernel.org/stable/c/21b8536aee819792f1b4b38b9aacf2a073025d49
- https://git.kernel.org/stable/c/642c6e73fce17fdca93a5793c4d22359fda866d7
- https://git.kernel.org/stable/c/cfb9d2976b277e554e28c165e3eff4b4a8ea10bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74710.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74710
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
