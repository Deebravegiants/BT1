# [C] RDMA/siw: bound Read Response placement to the RREAD length

## Summary
Severity: Critical
Advisory: CVE-2026-64268
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64268
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: bound Read Response placement to the RREAD length

In drivers/infiniband/sw/siw/siw_qp_rx.c, siw_proc_rresp() places each
inbound Read Response DDP segment at sge->laddr + wqe->processed and then
accumulates wqe->processed, but it never checks the running total against
the sink buffer length on continuation segments. siw_check_sge() resolves
and validates the sink memory only on the first fragment (the if (!*mem)
branch), and siw_rresp_check_ntoh() compares the cumulative length against
wqe->bytes only on the final segment (the !frx->more_ddp_segs guard).

A connected siw peer that answers an outstanding RREAD with Read Response
segments that keep the DDP Last flag clear, carrying more total payload
than the RREAD requested, drives wqe->processed past the validated sink
buffer; the next siw_rx_data() call writes out of bounds at
sge->laddr + wqe->processed. siw runs iWARP over ordinary routable TCP,
so the peer is the remote end of an established RDMA connection and needs
no local privilege.

Bound every segment before placement, exactly as siw_proc_send() and
siw_proc_write() already do for their tagged and untagged paths, and
terminate the connection with a base-or-bounds DDP error when the
Read Response would overrun the sink buffer.

This is the second receive-path length fix for this file. A separate
change rejects an MPA FPDU length that underflows the per-fragment
remainder in the header decode; that guard does not cover this case,
because here each individual segment length is self-consistent and only
the accumulated placement offset overruns the buffer.

## References
- https://git.kernel.org/stable/c/3ef7e052cbd05a8b13a51a07b185a39ec93ee1cf
- https://git.kernel.org/stable/c/423a78ff7928c2601013f73ec6d896f5597d0df5
- https://git.kernel.org/stable/c/595e6537ad1a210da32cbb9a7f91aa73090915ba
- https://git.kernel.org/stable/c/6bc89f34a4597f9f6d41f7a60c67a3153bfe8851
- https://git.kernel.org/stable/c/75c93cd3c421890f49ea93f0b978b9b7bb10e5e3
- https://git.kernel.org/stable/c/7d29f7e9dbd844cae4d3e559cf78324b9642fd6b
- https://git.kernel.org/stable/c/a31b6d18ded3cc32d9ee85a6ff0726d4274887b2
- https://git.kernel.org/stable/c/b2e26c955f8dd7e8d3f16c858db05245ea4fa817
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64268.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
