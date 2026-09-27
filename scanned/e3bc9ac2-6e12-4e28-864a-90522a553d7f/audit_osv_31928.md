# [M] xsk: fix an integer overflow in xp_create_and_assign_umem()

## Summary
Severity: Medium
Advisory: CVE-2025-21997
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-21997
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: fix an integer overflow in xp_create_and_assign_umem()

Since the i and pool->chunk_size variables are of type 'u32',
their product can wrap around and then be cast to 'u64'.
This can lead to two different XDP buffers pointing to the same
memory area.

Found by InfoTeCS on behalf of Linux Verification Center
(linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/130290f44bce0eead2b827302109afc3fe189ddd
- https://git.kernel.org/stable/c/205649d642a5b376724f04f3a5b3586815e43d3b
- https://git.kernel.org/stable/c/559847f56769037e5b2e0474d3dbff985b98083d
- https://git.kernel.org/stable/c/b7b4be1fa43294b50b22e812715198629806678a
- https://git.kernel.org/stable/c/c7670c197b0f1a8726ad5c87bc2bf001a1fc1bbd
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21997.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
