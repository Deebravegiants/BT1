# [C] rxrpc: Fix the ACK parser to extract the SACK table for parsing

## Summary
Severity: Critical
Advisory: CVE-2026-53151
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53151
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix the ACK parser to extract the SACK table for parsing

Fix modification of the received skbuff in rxrpc_input_soft_acks() and a
potential incorrect access of the buffer in a fragmented UDP packet (the
packet would probably have to be deliberately pre-generated as fragmented)
when AF_RXRPC tries to extract the contents of the SACK table by copying
out the contents of the SACK table into a buffer before attempting to parse

AF_RXRPC assumes that it can just call skb_condense() and then validly
access the SACK table from skb->data and that it will be a flat buffer -
but skb_condense() can silently fail to do anything under some
circumstances.

Note that whilst rxrpc_input_soft_acks() should be able to parse extended
ACKs, the rest of AF_RXRPC doesn't currently support that.

Further, there's then no need to call skb_condense() in rxrpc_input_ack(),
so don't.

## References
- https://git.kernel.org/stable/c/224298450be5c04d2a6ea1c2a94669d7ebf65d00
- https://git.kernel.org/stable/c/333b6d5bb9f87827ac2639c737bf9613dbae7253
- https://git.kernel.org/stable/c/566c4c1244de50fbff1f89ff93c9d7b0fc256db4
- https://git.kernel.org/stable/c/5d1ae4e17a3ecd8561cdb4f4f70152f41039c4e1
- https://git.kernel.org/stable/c/775c5e89272a2615b72bb84f611ba66fa3b7493e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53151.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53151
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
