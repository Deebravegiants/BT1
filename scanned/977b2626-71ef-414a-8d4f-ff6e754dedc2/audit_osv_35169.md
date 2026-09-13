# [C] net/handshake: duplicate handshake cancellations leak socket

## Summary
Severity: Critical
Advisory: CVE-2025-68775
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68775
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/handshake: duplicate handshake cancellations leak socket

When a handshake request is cancelled it is removed from the
handshake_net->hn_requests list, but it is still present in the
handshake_rhashtbl until it is destroyed.

If a second cancellation request arrives for the same handshake request,
then remove_pending() will return false... and assuming
HANDSHAKE_F_REQ_COMPLETED isn't set in req->hr_flags, we'll continue
processing through the out_true label, where we put another reference on
the sock and a refcount underflow occurs.

This can happen for example if a handshake times out - particularly if
the SUNRPC client sends the AUTH_TLS probe to the server but doesn't
follow it up with the ClientHello due to a problem with tlshd.  When the
timeout is hit on the server, the server will send a FIN, which triggers
a cancellation request via xs_reset_transport().  When the timeout is
hit on the client, another cancellation request happens via
xs_tls_handshake_sync().

Add a test_and_set_bit(HANDSHAKE_F_REQ_COMPLETED) in the pending cancel
path so duplicate cancels can be detected.

## References
- https://git.kernel.org/stable/c/011ae80c49d9bfa5b4336f8bd387cd25c7593663
- https://git.kernel.org/stable/c/15564bd67e2975002f2a8e9defee33e321d3183f
- https://git.kernel.org/stable/c/3c330f1dee3cd92b57e19b9d21dc8ce5970b09be
- https://git.kernel.org/stable/c/e1641177e7fb48a0a5a06658d4aab51da6656659
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68775.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68775
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
