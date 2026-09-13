# [H] xenbus: Use kref to track req lifetime

## Summary
Severity: High
Advisory: CVE-2025-37949
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37949
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.183, >=5.16.0 <6.1.139, >=6.2.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

xenbus: Use kref to track req lifetime

Marek reported seeing a NULL pointer fault in the xenbus_thread
callstack:
BUG: kernel NULL pointer dereference, address: 0000000000000000
RIP: e030:__wake_up_common+0x4c/0x180
Call Trace:
 <TASK>
 __wake_up_common_lock+0x82/0xd0
 process_msg+0x18e/0x2f0
 xenbus_thread+0x165/0x1c0

process_msg+0x18e is req->cb(req).  req->cb is set to xs_wake_up(), a
thin wrapper around wake_up(), or xenbus_dev_queue_reply().  It seems
like it was xs_wake_up() in this case.

It seems like req may have woken up the xs_wait_for_reply(), which
kfree()ed the req.  When xenbus_thread resumes, it faults on the zero-ed
data.

Linux Device Drivers 2nd edition states:
"Normally, a wake_up call can cause an immediate reschedule to happen,
meaning that other processes might run before wake_up returns."
... which would match the behaviour observed.

Change to keeping two krefs on each request.  One for the caller, and
one for xenbus_thread.  Each will kref_put() when finished, and the last
will free it.

This use of kref matches the description in
Documentation/core-api/kref.rst

## References
- https://git.kernel.org/stable/c/0e94a246bb6d9538010b6c02d2b1d4717a97b2e5
- https://git.kernel.org/stable/c/1f0304dfd9d217c2f8b04a9ef4b3258a66eedd27
- https://git.kernel.org/stable/c/2466b0f66795c3c426cacc8998499f38031dbb59
- https://git.kernel.org/stable/c/4d260a5558df4650eb87bc41b2c9ac2d6b2ba447
- https://git.kernel.org/stable/c/8b02f85e84dc6f7c150cef40ddb69af5a25659e5
- https://git.kernel.org/stable/c/8e9c8a0393b5f85f1820c565ab8105660f4e8f92
- https://git.kernel.org/stable/c/cbfaf46b88a4c01b64c4186cdccd766c19ae644c
- https://git.kernel.org/stable/c/f1bcac367bc95631afbb918348f30dec887d0e1b
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37949.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37949
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
