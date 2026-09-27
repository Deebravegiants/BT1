# [H] media: venus: fix use after free in vdec_close

## Summary
Severity: High
Advisory: CVE-2024-42313
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42313
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: fix use after free in vdec_close

There appears to be a possible use after free with vdec_close().
The firmware will add buffer release work to the work queue through
HFI callbacks as a normal part of decoding. Randomly closing the
decoder device from userspace during normal decoding can incur
a read after free for inst.

Fix it by cancelling the work in vdec_close.

## References
- https://git.kernel.org/stable/c/4c9d235630d35db762b85a4149bbb0be9d504c36
- https://git.kernel.org/stable/c/66fa52edd32cdbb675f0803b3c4da10ea19b6635
- https://git.kernel.org/stable/c/6a96041659e834dc0b172dda4b2df512d63920c2
- https://git.kernel.org/stable/c/72aff311194c8ceda934f24fd6f250b8827d7567
- https://git.kernel.org/stable/c/a0157b5aa34eb43ec4c5510f9c260bbb03be937e
- https://git.kernel.org/stable/c/ad8cf035baf29467158e0550c7a42b7bb43d1db6
- https://git.kernel.org/stable/c/da55685247f409bf7f976cc66ba2104df75d8dad
- https://git.kernel.org/stable/c/f8e9a63b982a8345470c225679af4ba86e4a7282
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42313.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42313
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
