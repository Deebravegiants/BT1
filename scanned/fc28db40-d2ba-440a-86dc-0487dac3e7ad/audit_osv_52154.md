# [H] CVE-2021-47137

## Summary
Severity: High
Advisory: CVE-2021-47137
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47137
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: lantiq: fix memory corruption in RX ring

In a situation where memory allocation or dma mapping fails, an
invalid address is programmed into the descriptor. This can lead
to memory corruption. If the memory allocation fails, DMA should
reuse the previous skb and mapping and drop the packet. This patch
also increments rx drop counter.

## References
- https://git.kernel.org/stable/c/5ac72351655f8b033a2935646f53b7465c903418
- https://git.kernel.org/stable/c/8bb1077448d43a871ed667520763e3b9f9b7975d
- https://git.kernel.org/stable/c/c7718ee96dbc2f9c5fc3b578abdf296dd44b9c20
- https://git.kernel.org/stable/c/46dd4abced3cb2c912916f4a5353e0927db0c4a2
