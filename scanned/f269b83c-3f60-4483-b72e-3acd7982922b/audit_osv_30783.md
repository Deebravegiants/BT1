# [M] ALSA: us122l: Use snd_card_free_when_closed() at disconnection

## Summary
Severity: Medium
Advisory: CVE-2024-56532
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56532
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: us122l: Use snd_card_free_when_closed() at disconnection

The USB disconnect callback is supposed to be short and not too-long
waiting.  OTOH, the current code uses snd_card_free() at
disconnection, but this waits for the close of all used fds, hence it
can take long.  It eventually blocks the upper layer USB ioctls, which
may trigger a soft lockup.

An easy workaround is to replace snd_card_free() with
snd_card_free_when_closed().  This variant returns immediately while
the release of resources is done asynchronously by the card device
release at the last close.

The loop of us122l->mmap_count check is dropped as well.  The check is
useless for the asynchronous operation with *_when_closed().

## References
- https://git.kernel.org/stable/c/020cbc4d7414f0962004213e2b7bc5cc607e9ec7
- https://git.kernel.org/stable/c/2938dd2648522336133c151dd67bb9bf01cbd390
- https://git.kernel.org/stable/c/75f418b249d84021865eaa59515d3ed9b75ce4d6
- https://git.kernel.org/stable/c/9a48bd2184b142c92a4e17eac074c61fcf975bc9
- https://git.kernel.org/stable/c/9b27924dc8d7f8a8c35e521287d4ccb9a006e597
- https://git.kernel.org/stable/c/9d5c530e4d70f64b1114f2cc29ac690ba7ac4a38
- https://git.kernel.org/stable/c/b7df09bb348016943f56b09dcaafe221e3f73947
- https://git.kernel.org/stable/c/bc778ad3e495333eebda36fe91d5b2c93109cc16
- https://git.kernel.org/stable/c/bf0aa35a7cb8602cccf2387712114e836f65c154
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56532.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56532
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
