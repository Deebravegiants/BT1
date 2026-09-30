# [H] sctp: detect and prevent references to a freed transport in sendmsg

## Summary
Severity: High
Advisory: CVE-2025-23142
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23142
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: detect and prevent references to a freed transport in sendmsg

sctp_sendmsg() re-uses associations and transports when possible by
doing a lookup based on the socket endpoint and the message destination
address, and then sctp_sendmsg_to_asoc() sets the selected transport in
all the message chunks to be sent.

There's a possible race condition if another thread triggers the removal
of that selected transport, for instance, by explicitly unbinding an
address with setsockopt(SCTP_SOCKOPT_BINDX_REM), after the chunks have
been set up and before the message is sent. This can happen if the send
buffer is full, during the period when the sender thread temporarily
releases the socket lock in sctp_wait_for_sndbuf().

This causes the access to the transport data in
sctp_outq_select_transport(), when the association outqueue is flushed,
to result in a use-after-free read.

This change avoids this scenario by having sctp_transport_free() signal
the freeing of the transport, tagging it as "dead". In order to do this,
the patch restores the "dead" bit in struct sctp_transport, which was
removed in
commit 47faa1e4c50e ("sctp: remove the dead field of sctp_transport").

Then, in the scenario where the sender thread has released the socket
lock in sctp_wait_for_sndbuf(), the bit is checked again after
re-acquiring the socket lock to detect the deletion. This is done while
holding a reference to the transport to prevent it from being freed in
the process.

If the transport was deleted while the socket lock was relinquished,
sctp_sendmsg_to_asoc() will return -EAGAIN to let userspace retry the
send.

The bug was found by a private syzbot instance (see the error report [1]
and the C reproducer that triggers it [2]).

## References
- https://git.kernel.org/stable/c/0f7df4899299ce4662e5f95badb9dbc57cc37fa5
- https://git.kernel.org/stable/c/2e5068b7e0ae0a54f6cfd03a2f80977da657f1ee
- https://git.kernel.org/stable/c/3257386be6a7eb8a8bfc9cbfb746df4eb4fc70e8
- https://git.kernel.org/stable/c/547762250220325d350d0917a7231480e0f4142b
- https://git.kernel.org/stable/c/5bc83bdf5f5b8010d1ca5a4555537e62413ab4e2
- https://git.kernel.org/stable/c/7a63f4fb0efb4e69efd990cbb740a848679ec4b0
- https://git.kernel.org/stable/c/9e7c37fadb3be1fc33073fcf10aa96d166caa697
- https://git.kernel.org/stable/c/c6fefcb71d246baaf3bacdad1af7ff50ebcfe652
- https://git.kernel.org/stable/c/f1a69a940de58b16e8249dff26f74c8cc59b32be
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23142.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23142
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
