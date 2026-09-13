# [C] RDMA/rtrs-srv: Bound RDMA-Write length to chunk size in rdma_write_sg

## Summary
Severity: Critical
Advisory: CVE-2026-64269
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64269
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.266, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs-srv: Bound RDMA-Write length to chunk size in rdma_write_sg

When the server answers an RTRS READ, rdma_write_sg() builds the source
scatter/gather entry for the IB_WR_RDMA_WRITE that returns data to the
peer. Its length is taken directly from the wire descriptor:

  plist->length = le32_to_cpu(id->rd_msg->desc[0].len);

rd_msg points into the chunk buffer that the remote peer filled via
RDMA-WRITE-WITH-IMM (rtrs_srv_rdma_done() -> process_io_req() ->
process_read()), so desc[0].len is attacker-controlled and, before this
change, was only rejected when zero. The source address is the fixed
chunk start (dma_addr[msg_id]) and the source lkey is the PD-wide
local_dma_lkey, which is not tied to the chunk's MR mapping, so the verbs
layer does not constrain the transfer length to max_chunk_size. msg_id
and off are bounded against queue_depth and max_chunk_size in
rtrs_srv_rdma_done(), but desc[0].len is a separate field that was not
checked against the chunk size.

A peer that advertises desc[0].len larger than max_chunk_size can make
the posted RDMA write read past the chunk's mapped region. The resulting
behaviour depends on the IOMMU configuration: with no IOMMU or in
passthrough mode the read may extend into memory adjacent to the chunk
and be returned to the peer, which can disclose host memory; with a
translating IOMMU the out-of-range access is expected to fault and abort
the connection. In either case the transfer exceeds what the protocol
permits and is driven by a remote peer.

Reject a descriptor length above max_chunk_size, mirroring the existing
off >= max_chunk_size bound in rtrs_srv_rdma_done(). Legitimate clients
do not exceed it: the client sets desc[0].len to its MR length, which is
capped at the negotiated max_io_size (max_chunk_size - MAX_HDR_SIZE).

## References
- https://git.kernel.org/stable/c/2912f3d40355dabc08fdbaaf2764d02445fe88dc
- https://git.kernel.org/stable/c/5a45d0aa1fa50a333ce5763ade744e2d89838667
- https://git.kernel.org/stable/c/68c09762172f6224e9ddf9b0a60bacbb36e443eb
- https://git.kernel.org/stable/c/6cada540150894e81042a0ae0c796a21a9a877da
- https://git.kernel.org/stable/c/6f40246f4312fdbab5a13cc440adebf95eb2aa66
- https://git.kernel.org/stable/c/963af8d97a8c6a117134a8d0db1415e0489200b1
- https://git.kernel.org/stable/c/a35b7a8728a53ddc80b323970689fa5985816836
- https://git.kernel.org/stable/c/da3e44add94b05dfde56f898421922f5cf35705f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64269.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
