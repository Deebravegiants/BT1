# [H] ALSA: pcm: Fix races among concurrent prealloc proc writes

## Summary
Severity: High
Advisory: CVE-2022-49288
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49288
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.14.279, >=4.15.0 <4.19.243, >=4.20.0 <5.4.193, >=5.5.0 <5.10.109, >=5.11.0 <5.15.32, >=5.16.0 <5.16.18, >=5.17.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: pcm: Fix races among concurrent prealloc proc writes

We have no protection against concurrent PCM buffer preallocation
changes via proc files, and it may potentially lead to UAF or some
weird problem.  This patch applies the PCM open_mutex to the proc
write operation for avoiding the racy proc writes and the PCM stream
open (and further operations).

## References
- https://git.kernel.org/stable/c/37b12c16beb6f6c1c3c678c1aacbc46525c250f7
- https://git.kernel.org/stable/c/51fce708ab8986a9879ee5da946a2cc120f1036d
- https://git.kernel.org/stable/c/5ed8f8e3c4e59d0396b9ccf2e639711e24295bb6
- https://git.kernel.org/stable/c/69534c48ba8ce552ce383b3dfdb271ffe51820c3
- https://git.kernel.org/stable/c/a21d2f323b5a978dedf9ff1d50f101f85e39b3f2
- https://git.kernel.org/stable/c/b560d670c87d7d40b3cf6949246fa4c7aa65a00a
- https://git.kernel.org/stable/c/e14dca613e0a6ddc2bf6e360f16936a9f865205b
- https://git.kernel.org/stable/c/e7786c445bb67a9a6e64f66ebd6b7215b153ff7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49288.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
