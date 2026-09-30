# [H] rxrpc: Fix recv-recv race of completed call

## Summary
Severity: High
Advisory: CVE-2025-38524
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38524
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.266, >=5.11.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix recv-recv race of completed call

If a call receives an event (such as incoming data), the call gets placed
on the socket's queue and a thread in recvmsg can be awakened to go and
process it.  Once the thread has picked up the call off of the queue,
further events will cause it to be requeued, and once the socket lock is
dropped (recvmsg uses call->user_mutex to allow the socket to be used in
parallel), a second thread can come in and its recvmsg can pop the call off
the socket queue again.

In such a case, the first thread will be receiving stuff from the call and
the second thread will be blocked on call->user_mutex.  The first thread
can, at this point, process both the event that it picked call for and the
event that the second thread picked the call for and may see the call
terminate - in which case the call will be "released", decoupling the call
from the user call ID assigned to it (RXRPC_USER_CALL_ID in the control
message).

The first thread will return okay, but then the second thread will wake up
holding the user_mutex and, if it sees that the call has been released by
the first thread, it will BUG thusly:

	kernel BUG at net/rxrpc/recvmsg.c:474!

Fix this by just dequeuing the call and ignoring it if it is seen to be
already released.  We can't tell userspace about it anyway as the user call
ID has become stale.

## References
- https://git.kernel.org/stable/c/4aed0eeca58e26d752bb08b293b8dc75c6820b23
- https://git.kernel.org/stable/c/6c75a97a32a5fa2060c3dd30207e63b6914b606d
- https://git.kernel.org/stable/c/7692bde890061797f3dece0148d7859e85c55778
- https://git.kernel.org/stable/c/839fe96c15209dc2255c064bb44b636efe04f032
- https://git.kernel.org/stable/c/962fb1f651c2cf2083e0c3ef53ba69e3b96d3fbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38524.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38524
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
