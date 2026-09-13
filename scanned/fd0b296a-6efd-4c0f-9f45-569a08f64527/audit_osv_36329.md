# [H] rxrpc: Fix recvmsg() unconditional requeue

## Summary
Severity: High
Advisory: CVE-2026-23066
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23066
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix recvmsg() unconditional requeue

If rxrpc_recvmsg() fails because MSG_DONTWAIT was specified but the call at
the front of the recvmsg queue already has its mutex locked, it requeues
the call - whether or not the call is already queued.  The call may be on
the queue because MSG_PEEK was also passed and so the call was not dequeued
or because the I/O thread requeued it.

The unconditional requeue may then corrupt the recvmsg queue, leading to
things like UAFs or refcount underruns.

Fix this by only requeuing the call if it isn't already on the queue - and
moving it to the front if it is already queued.  If we don't queue it, we
have to put the ref we obtained by dequeuing it.

Also, MSG_PEEK doesn't dequeue the call so shouldn't call
rxrpc_notify_socket() for the call if we didn't use up all the data on the
queue, so fix that also.

## References
- https://git.kernel.org/stable/c/0464bf75590da75b8413c3e758c04647b4cdb3c6
- https://git.kernel.org/stable/c/2c28769a51deb6022d7fbd499987e237a01dd63a
- https://git.kernel.org/stable/c/8fd3b5e297854a4da0f273169baf4b1b7b257b97
- https://git.kernel.org/stable/c/930114425065f7ace6e0c0630fab4af75e059ea8
- https://git.kernel.org/stable/c/c198628f3fca5c874d93874c233014d336e09f64
- https://git.kernel.org/stable/c/c6cebcb4e0b3140ec2ace45c020a9049527385d1
- https://git.kernel.org/stable/c/cf969bddd6e69c5777fa89dc88402204e72f312a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23066.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23066
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
