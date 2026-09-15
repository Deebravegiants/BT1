# [H] RDMA/rxe: Reject unknown opcodes before ICRC processing

## Summary
Severity: High
Advisory: CVE-2026-46133
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46133
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Reject unknown opcodes before ICRC processing

Even after applying commit 7244491dab34 ("RDMA/rxe: Validate pad and ICRC
before payload_size() in rxe_rcv"), a single unauthenticated UDP packet
can still trigger panic.  That patch handled payload_size() underflow only
for valid opcodes with short packets, not for packets carrying an unknown
opcode.  The unknown-opcode OOB read described below predates that commit
and reaches back to the initial Soft RoCE driver.

The check added there reads

    pkt->paylen < header_size(pkt) + bth_pad(pkt) + RXE_ICRC_SIZE

where header_size(pkt) expands to rxe_opcode[pkt->opcode].length.  The
rxe_opcode[] array has 256 entries but is only populated for defined IB
opcodes; any other entry (for example opcode 0xff) is zero-initialized, so
length == 0 and the check degenerates to

    pkt->paylen < 0 + bth_pad(pkt) + RXE_ICRC_SIZE

which does not constrain pkt->paylen enough.  rxe_icrc_hdr() then computes

    rxe_opcode[pkt->opcode].length - RXE_BTH_BYTES

which underflows when length == 0 and passes a huge value to rxe_crc32(),
causing an out-of-bounds read of the skb payload.

Reproduced on v7.0-rc7 with that fix applied, QEMU/KVM with
CONFIG_RDMA_RXE=y and CONFIG_KASAN=y, after

    rdma link add rxe0 type rxe netdev eth0

A single 48-byte UDP packet to port 4791 with BTH opcode=0xff and
QPN=IB_MULTICAST_QPN triggers:

    BUG: KASAN: slab-out-of-bounds in crc32_le+0x115/0x170
    Read of size 1 at addr ...
    The buggy address is located 0 bytes to the right of
     allocated 704-byte region
    Call Trace:
     crc32_le+0x115/0x170
     rxe_icrc_hdr.isra.0+0x226/0x300
     rxe_icrc_check+0x13f/0x3a0
     rxe_rcv+0x6e1/0x16e0
     rxe_udp_encap_recv+0x20a/0x320
     udp_queue_rcv_one_skb+0x7ed/0x12c0

Subsequent packets with the same shape fault on unmapped memory and panic
the kernel.  The trigger requires only module load and "rdma link add"; no
QP, no connection, and no authentication.

Fix this by rejecting packets whose opcode has no rxe_opcode[] entry,
detected via the zero mask or zero length, before any length arithmetic
runs.

## References
- https://git.kernel.org/stable/c/006a3a5f75345c6a0dbf13fd3ee01406e93b6733
- https://git.kernel.org/stable/c/318787fa7193bd79691f2ebce4e80cb6abd0faef
- https://git.kernel.org/stable/c/4c6f86d85d03cdb33addce86aa69aa795ca6c47a
- https://git.kernel.org/stable/c/599cfdf44c1701c581cd4a21f1e1e03f8dc3840b
- https://git.kernel.org/stable/c/6a79b1ea0fcb2c998fda6a793050f66146e9cc42
- https://git.kernel.org/stable/c/6fa18025e5782afff91415fd5217b39c1e4837d7
- https://git.kernel.org/stable/c/e3dc3a2fb05f4ed49c7f20594c4c52350d032189
- https://git.kernel.org/stable/c/f8ee926431a7bbec2b10c1290664af2cb290b983
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46133.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46133
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
