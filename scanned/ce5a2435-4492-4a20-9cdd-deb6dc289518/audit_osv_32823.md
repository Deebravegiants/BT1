# [H] ALSA: pcm: Fix race of buffer access at PCM OSS layer

## Summary
Severity: High
Advisory: CVE-2025-38078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38078
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Fix race of buffer access at PCM OSS layer

The PCM OSS layer tries to clear the buffer with the silence data at
initialization (or reconfiguration) of a stream with the explicit call
of snd_pcm_format_set_silence() with runtime->dma_area.  But this may
lead to a UAF because the accessed runtime->dma_area might be freed
concurrently, as it's performed outside the PCM ops.

For avoiding it, move the code into the PCM core and perform it inside
the buffer access lock, so that it won't be changed during the
operation.

## References
- https://git.kernel.org/stable/c/10217da9644ae75cea7330f902c35fc5ba78bbbf
- https://git.kernel.org/stable/c/74d90875f3d43f3eff0e9861c4701418795d3455
- https://git.kernel.org/stable/c/8170d8ec4efd0be352c14cb61f374e30fb0c2a25
- https://git.kernel.org/stable/c/93a81ca0657758b607c3f4ba889ae806be9beb73
- https://git.kernel.org/stable/c/afa56c960fcb4db37f2e3399f28e9402e4e1f470
- https://git.kernel.org/stable/c/bf85e49aaf3a3c5775ea87369ea5f159c2148db4
- https://git.kernel.org/stable/c/c0e05a76fc727929524ef24a19c302e6dd40233f
- https://git.kernel.org/stable/c/f3e14d706ec18faf19f5a6e75060e140fea05d4a
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38078.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
