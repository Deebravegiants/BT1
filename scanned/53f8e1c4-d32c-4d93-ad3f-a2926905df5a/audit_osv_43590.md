# [C] rxrpc: Don't move a peeked OOB message onto the pending queue

## Summary
Severity: Critical
Advisory: CVE-2026-74434
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74434
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Don't move a peeked OOB message onto the pending queue

rxrpc_recvmsg_oob() takes a received oob message off recvmsg_oobq and,
if a response is needed, moves it onto the pending_oobq tree. However,
only the unlink from recvmsg_oobq is guarded by MSG_PEEK; the move onto
pending_oobq always runs.

As a result, reading a challenge with MSG_PEEK leaves the skb on
recvmsg_oobq while also adding it to pending_oobq. Since struct
sk_buff's rbnode shares storage with its next and prev pointers,
rb_insert_color() overwrites the list linkage, and the skb, which holds
a single reference, becomes reachable from both queues at once.

When the socket is closed both queues are drained in turn. While
draining recvmsg_oobq, __skb_unlink() follows the next and prev
pointers that rbnode has overwritten and writes to a bad address. Also,
as the skb holds a single reference but is freed from each queue, both
the skb and the connection reference it holds are released twice. This
leads to memory corruption and to a use-after-free caused by the
connection refcount underflow.

MSG_PEEK does not consume the message from the queue, so only unlink it
from recvmsg_oobq and then move it onto pending_oobq or free it when
the message is actually consumed.

## References
- https://git.kernel.org/stable/c/5801cff7d5d7b4e9d877dfb627b23eb63167f02c
- https://git.kernel.org/stable/c/5f470cc883416fea6d3bce18ef96bf91dd49ffc3
- https://git.kernel.org/stable/c/9ada3931beb37068fcb725b34b0398457009f343
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74434.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74434
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
