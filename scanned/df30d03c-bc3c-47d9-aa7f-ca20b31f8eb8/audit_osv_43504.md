# [H] tipc: prevent snt_unacked underflow on CONN_ACK

## Summary
Severity: High
Advisory: CVE-2026-74282
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74282
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: prevent snt_unacked underflow on CONN_ACK

tipc_sk_conn_proto_rcv() subtracts the peer-supplied connection ack count
from the unsigned 16-bit send counter snt_unacked without checking that it
does not exceed the number of messages actually outstanding:

	tsk->snt_unacked -= msg_conn_ack(hdr);

msg_conn_ack() is read straight from a received CONN_MANAGER/CONN_ACK
message. If the ack count is larger than snt_unacked, the subtraction
wraps to a near-maximum value, leaving tsk_conn_cong() permanently true
and starving the connection of further transmits.

Validate the ACK count at the start of the CONN_ACK block and drop the
message if it acknowledges more messages than are outstanding. A peer (or,
for a local connection, the connected peer socket) can otherwise wedge a
TIPC connection's send side by sending an oversized connection ack.

## References
- https://git.kernel.org/stable/c/1e2c956745777e6ffdee7f30da5935741c03ee1e
- https://git.kernel.org/stable/c/3388145d258cf2c4c98278e3987296007d30672e
- https://git.kernel.org/stable/c/3cfa3d8e0dc167850edeb5bf5a07757db83fd54e
- https://git.kernel.org/stable/c/47ed873e4ceda34098bd46d8e96b4bb13cad3a04
- https://git.kernel.org/stable/c/67e55b054bf8025658dc0e255057f2a6236416bd
- https://git.kernel.org/stable/c/96f91b8ae1a489b3eca137e7acf42cf985fb8939
- https://git.kernel.org/stable/c/ab3e10b44ba5411779aac7afd2477917dd77750f
- https://git.kernel.org/stable/c/b44bebdd32c9ff66ee2aebfc317ced44bedd9335
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74282.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
