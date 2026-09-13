# [H] rxrpc: Fix ACKALL packet handling

## Summary
Severity: High
Advisory: CVE-2026-74430
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74430
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix ACKALL packet handling

rxrpc_input_ackall() accepts ACKALL packets without checking whether the
call is in a state that can legitimately have outstanding transmit buffers.
A forged ACKALL can therefore reach a new service call in
RXRPC_CALL_SERVER_RECV_REQUEST before any reply packets have been queued.

In that state call->tx_top is zero and call->tx_queue is NULL, so
rxrpc_rotate_tx_window() dereferences a NULL txqueue and triggers a
null-pointer dereference.

Fix the handling of ACKALL packets by the following means:

 (1) Add two new call states: RXRPC_CALL_CLIENT_PRE_SEND which indicates
     that the client call is connected, but nothing has been transmitted as
     yet; and RXRPC_CALL_CLIENT_AWAIT_ACK, which indicates that everything
     has been transmitted at least once, but we're now waiting for the
     stuff remaining in the Tx buffer to be ACK'd (retransmissions may
     still happen).

     The RXRPC_CALL_CLIENT_PRE_SEND state is set when the call is assigned
     a channel and transitions to RXRPC_CALL_CLIENT_SEND_REQUEST when the
     first packet is transmitted.

     RXRPC_CALL_CLIENT_AWAIT_REPLY is then narrowed in scope to indicate
     that all Tx packets have been ACK'd and we're now waiting for the
     reply to be received.

 (2) As per Wyatt Feng's original patch[1], the ACKALL handler then checks
     that the call state is one in which there might be stuff in the Tx
     buffer to ACK, but now this includes AWAIT_ACK rather than
     AWAIT_REPLY.  ACKALL packets are ignored if received in the wrong
     state.

     Note that unlike Wyatt Feng's patch, it's no longer necessary to check
     to see if the Tx buffer exists as this the state set now covers this.

 (3) Make the ACKALL handler use call->tx_transmitted rather than
     call->tx_top as the former is explicitly the highest packet seq number
     transmitted, whereas the latter has a looser definition.

Thanks to Jeffrey Altman for a description of the history of the ACKALL
packet[1].

## References
- https://git.kernel.org/stable/c/523cb585672ae681b2d3b0d620aec5313774e2e2
- https://git.kernel.org/stable/c/8db6a2c95e36938076b37466ce36774526a5c8c3
- https://git.kernel.org/stable/c/9b6ce594808580b2a19e6e1aa459ef56c0153ac1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74430.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74430
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
