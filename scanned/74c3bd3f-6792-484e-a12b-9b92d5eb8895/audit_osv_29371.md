# [H] IB/core: Implement a limit on UMAD receive List

## Summary
Severity: High
Advisory: CVE-2024-42145
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42145
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.98, >=6.2.0 <6.6.39, >=6.7.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/core: Implement a limit on UMAD receive List

The existing behavior of ib_umad, which maintains received MAD
packets in an unbounded list, poses a risk of uncontrolled growth.
As user-space applications extract packets from this list, the rate
of extraction may not match the rate of incoming packets, leading
to potential list overflow.

To address this, we introduce a limit to the size of the list. After
considering typical scenarios, such as OpenSM processing, which can
handle approximately 100k packets per second, and the 1-second retry
timeout for most packets, we set the list size limit to 200k. Packets
received beyond this limit are dropped, assuming they are likely timed
out by the time they are handled by user-space.

Notably, packets queued on the receive list due to reasons like
timed-out sends are preserved even when the list is full.

## References
- https://git.kernel.org/stable/c/1288cf1cceb0e6df276e182f5412370fb4169bcb
- https://git.kernel.org/stable/c/62349fbf86b5e13b02721bdadf98c29afd1e7b5f
- https://git.kernel.org/stable/c/63d202d948bb6d3a28cd8e8b96b160fa53e18baa
- https://git.kernel.org/stable/c/a6627fba793cc75b7365d9504a0095fb2902dda4
- https://git.kernel.org/stable/c/b4913702419d064ec4c4bbf7270643c95cc89a1b
- https://git.kernel.org/stable/c/b8c5f635997f49c625178d1a0cb32a80ed33abe6
- https://git.kernel.org/stable/c/ca0b44e20a6f3032224599f02e7c8fb49525c894
- https://git.kernel.org/stable/c/d73cb8862e4d6760ccc94d3b57b9ef6271400607
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42145.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42145
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
