# [H] afs: Fix UAF when sending a message

## Summary
Severity: High
Advisory: CVE-2026-74506
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74506
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

afs: Fix UAF when sending a message

In afs_make_call(), there's a race with async call reception and
destruction.  If a call is dispatched that doesn't have call->write_iter
set (used to specify the data content for FS.StoreData), then the first
rxrpc_kernel_send_data() will not set MSG_MORE in the msghdr.

Once rxrpc_send_data() queues the last request packet, the response could
come in at any time and cause the call to be completed and put.  However,
afs_make_call() will look at the call again to see it ->write_iter should
be handled - something it's only allowed to do if it has its own ref on the
call.  Whilst this is the case for synchronous calls, it isn't true for
async calls such as FS.FetchData.

There's also a potential UAF in afs_make_call() in the event that an
asynchronous call is being sent, but the call fails in some way (e.g. it
gets aborted from the server).  The problem there is that afs_make_call()
tries to abort a call if the rxrpc send fails, but the asynchronous
notification from rxrpc may have caused the afs_call to be torn down.

generic/650 plays games with randomly taking CPUs offline, and can
interject a significant delay such that the call is deallocated before
afs_make_call() gets to check call->write_iter - and a UAF ensues (caught
by KASAN).

   BUG: KASAN: slab-use-after-free in afs_make_call+0x1c90/0x2210 [kafs]
   Read of size 8 at addr ffff888035e050e8 by task fsstress/1409

Fix this by making afs_make_op_call() give the op->call its own ref rather
than transferring the caller's ref to it and then dropping the ref when
afs_make_call() returns.

This also means that the afs_make_call() func never loses its ref on the
call now.

## References
- https://git.kernel.org/stable/c/4af1ec68d54b3871155914d584fb10669c41a861
- https://git.kernel.org/stable/c/c0d3b81f703b2a9e37fe1347610a50cdf0078c27
- https://git.kernel.org/stable/c/daaa726b14fc3026a6b328614d312b698f62f391
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74506.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74506
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
