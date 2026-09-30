# [H] RDMA/rxe: Reject non-8-byte ATOMIC_WRITE payloads

## Summary
Severity: High
Advisory: CVE-2026-46114
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46114
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Reject non-8-byte ATOMIC_WRITE payloads

atomic_write_reply() at drivers/infiniband/sw/rxe/rxe_resp.c
unconditionally dereferences 8 bytes at payload_addr(pkt):

    value = *(u64 *)payload_addr(pkt);

check_rkey() previously accepted an ATOMIC_WRITE request with pktlen ==
resid == 0 because the length validation only compared pktlen against
resid. A remote initiator that sets the RETH length to 0 therefore reaches
atomic_write_reply() with a zero-byte logical payload, and the responder
reads sizeof(u64) bytes from past the logical end of the packet into
skb->head tailroom, then writes those 8 bytes into the attacker's MR via
rxe_mr_do_atomic_write(). That is a remote disclosure of 4 bytes of kernel
tailroom per probe (the other 4 bytes are the packet's own trailing ICRC).

IBA oA19-28 defines ATOMIC_WRITE as exactly 8 bytes. Anything else is
protocol-invalid. Hoist a strict length check into check_rkey() so the
responder never reaches the unchecked dereference, and keep the existing
WRITE-family length logic for the normal RDMA WRITE path.

Reproduced on mainline with an unmodified rxe driver: a sustained
zero-length ATOMIC_WRITE probe repeatedly leaks adjacent skb head-buffer
bytes into the attacker's MR, including recognisable kernel strings and
partial kernel-direct-map pointer words.  With this patch applied the
responder rejects the PDU and the MR stays all-zero.

## References
- https://git.kernel.org/stable/c/105bf79a23b85cf3a761d18a4f3e10ce88526bc1
- https://git.kernel.org/stable/c/1114c87aa6f195cf07da55a27b2122ae26557b26
- https://git.kernel.org/stable/c/539cabb7b2d8ba70f55bba91db55faef11c2a6d7
- https://git.kernel.org/stable/c/7ec1ed4747f5f99f8b797bb438c5efd36079fad5
- https://git.kernel.org/stable/c/d415fce3fcde6d7aeea6c25362a395b905811452
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46114.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
