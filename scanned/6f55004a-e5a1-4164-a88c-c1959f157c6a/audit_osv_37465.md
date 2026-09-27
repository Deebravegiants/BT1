# [H] tipc: fix bc_ackers underflow on duplicate GRP_ACK_MSG

## Summary
Severity: High
Advisory: CVE-2026-31662
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31662
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix bc_ackers underflow on duplicate GRP_ACK_MSG

The GRP_ACK_MSG handler in tipc_group_proto_rcv() currently decrements
bc_ackers on every inbound group ACK, even when the same member has
already acknowledged the current broadcast round.

Because bc_ackers is a u16, a duplicate ACK received after the last
legitimate ACK wraps the counter to 65535. Once wrapped,
tipc_group_bc_cong() keeps reporting congestion and later group
broadcasts on the affected socket stay blocked until the group is
recreated.

Fix this by ignoring duplicate or stale ACKs before touching bc_acked or
bc_ackers. This makes repeated GRP_ACK_MSG handling idempotent and
prevents the underflow path.

## References
- https://git.kernel.org/stable/c/1b6f13f626665cac67ba5a012765427680518711
- https://git.kernel.org/stable/c/36ec4fdd6250dcd5e73eb09ea92ed92e9cc28412
- https://git.kernel.org/stable/c/3bcf7aca63f0bcd679ae28e9b99823c608e59ce3
- https://git.kernel.org/stable/c/48a5fe38772b6f039522469ee6131a67838221a8
- https://git.kernel.org/stable/c/575faea557f1a184a5f09661bd47ebd3ef3769f8
- https://git.kernel.org/stable/c/a2ea1ef0167d7a84730638d05c20ccdc421b14b6
- https://git.kernel.org/stable/c/a7db57ccca21f5801609065473c89a38229ecb92
- https://git.kernel.org/stable/c/e0bb732eaf77f9ac2f2638bdac9e39b81e0a9682
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31662.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
