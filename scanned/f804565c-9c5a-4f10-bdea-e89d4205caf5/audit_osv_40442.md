# [C] net: mvpp2: refill RX buffers before XDP or skb use

## Summary
Severity: Critical
Advisory: CVE-2026-53215
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53215
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mvpp2: refill RX buffers before XDP or skb use

The RX error path returns the current descriptor buffer to the hardware
BM pool. That is only valid while the driver still owns the buffer.

mvpp2_rx_refill() can fail after the current buffer has been handed to
XDP or attached to an skb. In those cases mvpp2_run_xdp() may have
recycled, redirected, or queued the page for XDP_TX, and an skb free also
retires the data buffer. Returning such a buffer to BM lets hardware DMA
into memory that is no longer owned by the RX ring.

Refill the BM pool before handing the current buffer to XDP or to the
skb. If the allocation fails there, drop the packet and return the
still-owned current buffer to BM, preserving the pool depth. Once the
refill succeeds, later local drops retire/free the current buffer instead
of returning it to BM.

## References
- https://git.kernel.org/stable/c/02e1b5c4d3b4c658b72c145427cded1bba613fc1
- https://git.kernel.org/stable/c/580f92f27cb8724bcc4be98ee89890eab524a2ae
- https://git.kernel.org/stable/c/5e8e2a9624df72fca7c736b2966b2cbf6c9c3ff6
- https://git.kernel.org/stable/c/8a2126c5afe89f8ceeb60a3afb9f075b736194cd
- https://git.kernel.org/stable/c/a03cdcedb2cbcc42551dc3e4746929e93c5352d5
- https://git.kernel.org/stable/c/a88b3293b556f4d8fba11db9a8061a6b0d3b69e6
- https://git.kernel.org/stable/c/d0c8c4fbd22d260fe28530260656c5fb3c20ce84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53215
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
