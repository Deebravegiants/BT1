# [H] RDMA/rxe: Fix incomplete state save in rxe_requester

## Summary
Severity: High
Advisory: CVE-2023-53539
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53539
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix incomplete state save in rxe_requester

If a send packet is dropped by the IP layer in rxe_requester()
the call to rxe_xmit_packet() can fail with err == -EAGAIN.
To recover, the state of the wqe is restored to the state before
the packet was sent so it can be resent. However, the routines
that save and restore the state miss a significnt part of the
variable state in the wqe, the dma struct which is used to process
through the sge table. And, the state is not saved before the packet
is built which modifies the dma struct.

Under heavy stress testing with many QPs on a fast node sending
large messages to a slow node dropped packets are observed and
the resent packets are corrupted because the dma struct was not
restored. This patch fixes this behavior and allows the test cases
to succeed.

## References
- https://git.kernel.org/stable/c/255c0e60e1d16874fc151358d94bc8df661600dd
- https://git.kernel.org/stable/c/2f2a6422287fe29f9343247d77b645100ece0652
- https://git.kernel.org/stable/c/5d122db2ff80cd2aed4dcd630befb56b51ddf947
- https://git.kernel.org/stable/c/70518f3aaf5a059b691867d7d2d46b999319656a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53539.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53539
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
