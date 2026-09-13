# [H] tun: free page on short-frame rejection in tun_xdp_one()

## Summary
Severity: High
Advisory: CVE-2026-46321
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46321
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.11.0 <6.18.35, >=6.13.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tun: free page on short-frame rejection in tun_xdp_one()

tun_xdp_one() returns -EINVAL on a frame shorter than ETH_HLEN without
freeing the page that vhost_net_build_xdp() allocated for it.
tun_sendmsg() discards that -EINVAL and still returns total_len, so
vhost_tx_batch() takes the success path and never frees the page; each
short frame in a batch leaks one page-frag chunk.

A local process that can open /dev/net/tun and /dev/vhost-net can hit
this path: it attaches a tun/tap device as the vhost-net backend and
feeds TX descriptors whose length minus the virtio-net header is below
ETH_HLEN. Each kick leaks the page-frag chunks for that batch, and a
tight submission loop exhausts host memory and triggers an OOM panic.
Free the page before returning -EINVAL, matching the XDP-program error
path in the same function.

## References
- https://git.kernel.org/stable/c/0a6f46a9332ad6958992d64d3b3a81a80b2ca940
- https://git.kernel.org/stable/c/0e8211fcf9426f5adddf32516ba0f400ceb9544d
- https://git.kernel.org/stable/c/37a1c268c2c8090bf4dc552d732bd23ba36f8eb0
- https://git.kernel.org/stable/c/5b34f9e4fe2f203724a6e893d6df0316b9670057
- https://git.kernel.org/stable/c/69863ff2720a0e9871f1a5710f2a33a94217fee0
- https://git.kernel.org/stable/c/98c67be9eb9de72465a071949e84a3cdb8fab5a3
- https://git.kernel.org/stable/c/e915445942af6dcea628bf66d6241641201a0c41
- https://git.kernel.org/stable/c/f4feb1e20058e407cb00f45aff47f5b7e19a6bbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46321.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
