# [H] ALSA: usb-audio: Fix potential overflow of PCM transfer buffer

## Summary
Severity: High
Advisory: CVE-2025-40269
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-06
Source: https://osv.dev/vulnerability/CVE-2025-40269
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.4.230, >=4.5.0 <4.9.230, >=4.10.0 <4.14.188, >=4.15.0 <4.19.132, >=4.20.0 <5.4.51, >=5.5.0 <5.7.8, >=5.8.0 <5.15.197, >=5.11.0 <6.1.159, >=5.16.0 <6.6.117, >=6.2.0 <6.12.59, >=6.7.0 <6.17.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: usb-audio: Fix potential overflow of PCM transfer buffer

The PCM stream data in USB-audio driver is transferred over USB URB
packet buffers, and each packet size is determined dynamically.  The
packet sizes are limited by some factors such as wMaxPacketSize USB
descriptor.  OTOH, in the current code, the actually used packet sizes
are determined only by the rate and the PPS, which may be bigger than
the size limit above.  This results in a buffer overflow, as reported
by syzbot.

Basically when the limit is smaller than the calculated packet size,
it implies that something is wrong, most likely a weird USB
descriptor.  So the best option would be just to return an error at
the parameter setup time before doing any further operations.

This patch introduces such a sanity check, and returns -EINVAL when
the packet size is greater than maxpacksize.  The comparison with
ep->packsize[1] alone should suffice since it's always equal or
greater than ep->packsize[0].

## References
- https://git.kernel.org/stable/c/05a1fc5efdd8560f34a3af39c9cf1e1526cc3ddf
- https://git.kernel.org/stable/c/217d47255a2ec8b246f2725f5db9ac3f1d4109d7
- https://git.kernel.org/stable/c/282aba56713bbc58155716b55ca7222b2d9cf3c8
- https://git.kernel.org/stable/c/480a1490c595a242f27493a4544b3efb21b29f6a
- https://git.kernel.org/stable/c/6a5da3fa80affc948923f20a4e086177f505e86e
- https://git.kernel.org/stable/c/98e9d5e33bda8db875cc1a4fe99c192658e45ab6
- https://git.kernel.org/stable/c/ab0b5e92fc36ee82c1bd01fe896d0f775ed5de41
- https://git.kernel.org/stable/c/c4dc012b027c9eb101583011089dea14d744e314
- https://git.kernel.org/stable/c/d2c04f20ccc6c0d219e6d3038bab45bc66a178ad
- https://git.kernel.org/stable/c/d67dde02049e632ba58d3c44a164a74b6a737154
- https://git.kernel.org/stable/c/e0ed5a36fb3ab9e7b9ee45cd17f09f6d5f594360
- https://git.kernel.org/stable/c/ece3b981bb6620e47fac826a2156c090b1a936a0
- https://git.kernel.org/stable/c/ef592bf2232a2daa9fffa8881881fc9957ea56e9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40269.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
