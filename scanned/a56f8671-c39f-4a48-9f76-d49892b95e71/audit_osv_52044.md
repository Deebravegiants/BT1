# [M] CVE-2021-47001

## Summary
Severity: Medium
Advisory: CVE-2021-47001
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47001
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Fix cwnd update ordering

After a reconnect, the reply handler is opening the cwnd (and thus
enabling more RPC Calls to be sent) /before/ rpcrdma_post_recvs()
can post enough Receive WRs to receive their replies. This causes an
RNR and the new connection is lost immediately.

The race is most clearly exposed when KASAN and disconnect injection
are enabled. This slows down rpcrdma_rep_create() enough to allow
the send side to post a bunch of RPC Calls before the Receive
completion handler can invoke ib_post_recv().

## References
- https://security.netapp.com/advisory/ntap-20250411-0001/
- https://git.kernel.org/stable/c/8834ecb5df22b7ff3c9b0deba7726579bb613f95
- https://git.kernel.org/stable/c/eddae8be7944096419c2ae29477a45f767d0fcd4
- https://git.kernel.org/stable/c/19b5fa9489b5706bc878c3a522a7f771079e2fa0
- https://git.kernel.org/stable/c/35d8b10a25884050bb3b0149b62c3818ec59f77c
