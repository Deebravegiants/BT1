# [H] net: ethernet: cortina: Use TOE/TSO on all TCP

## Summary
Severity: High
Advisory: CVE-2025-38331
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38331
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: cortina: Use TOE/TSO on all TCP

It is desireable to push the hardware accelerator to also
process non-segmented TCP frames: we pass the skb->len
to the "TOE/TSO" offloader and it will handle them.

Without this quirk the driver becomes unstable and lock
up and and crash.

I do not know exactly why, but it is probably due to the
TOE (TCP offload engine) feature that is coupled with the
segmentation feature - it is not possible to turn one
part off and not the other, either both TOE and TSO are
active, or neither of them.

Not having the TOE part active seems detrimental, as if
that hardware feature is not really supposed to be turned
off.

The datasheet says:

  "Based on packet parsing and TCP connection/NAT table
   lookup results, the NetEngine puts the packets
   belonging to the same TCP connection to the same queue
   for the software to process. The NetEngine puts
   incoming packets to the buffer or series of buffers
   for a jumbo packet. With this hardware acceleration,
   IP/TCP header parsing, checksum validation and
   connection lookup are offloaded from the software
   processing."

After numerous tests with the hardware locking up after
something between minutes and hours depending on load
using iperf3 I have concluded this is necessary to stabilize
the hardware.

## References
- https://git.kernel.org/stable/c/1b503b790109d19710ec83c589c3ee59e95347ec
- https://git.kernel.org/stable/c/2bd434bb0eeb680c2b3dd6c68ca319b30cb8d47f
- https://git.kernel.org/stable/c/6a07e3af4973402fa199a80036c10060b922c92c
- https://git.kernel.org/stable/c/a37888a435b0737128d2d9c6f67b8d608f83df7a
- https://git.kernel.org/stable/c/ebe12e232f1d58ebb4b53b6d9149962b707bed91
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38331.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38331
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
