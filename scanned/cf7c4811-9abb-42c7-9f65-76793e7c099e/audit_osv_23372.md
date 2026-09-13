# [M] vt: fix memory overlapping when deleting chars in the buffer

## Summary
Severity: Medium
Advisory: CVE-2022-48627
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2022-48627
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

vt: fix memory overlapping when deleting chars in the buffer

A memory overlapping copy occurs when deleting a long line. This memory
overlapping copy can cause data corruption when scr_memcpyw is optimized
to memcpy because memcpy does not ensure its behavior if the destination
buffer overlaps with the source buffer. The line buffer is not always
broken, because the memcpy utilizes the hardware acceleration, whose
result is not deterministic.

Fix this problem by using replacing the scr_memcpyw with scr_memmovew.

## References
- https://git.kernel.org/stable/c/14d2cc21ca622310babf373e3a8f0b40acfe8265
- https://git.kernel.org/stable/c/39cdb68c64d84e71a4a717000b6e5de208ee60cc
- https://git.kernel.org/stable/c/57964a5710252bc82fe22d9fa98c180c58c20244
- https://git.kernel.org/stable/c/815be99d934e3292906536275f2b8d5131cdf52c
- https://git.kernel.org/stable/c/bfee93c9a6c395f9aa62268f1cedf64999844926
- https://git.kernel.org/stable/c/c8686c014b5e872ba7e334f33ca553f14446fc29
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48627.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
