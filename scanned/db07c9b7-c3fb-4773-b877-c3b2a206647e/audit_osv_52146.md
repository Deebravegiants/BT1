# [M] CVE-2021-47124

## Summary
Severity: Medium
Advisory: CVE-2021-47124
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47124
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: fix link timeout refs

WARNING: CPU: 0 PID: 10242 at lib/refcount.c:28 refcount_warn_saturate+0x15b/0x1a0 lib/refcount.c:28
RIP: 0010:refcount_warn_saturate+0x15b/0x1a0 lib/refcount.c:28
Call Trace:
 __refcount_sub_and_test include/linux/refcount.h:283 [inline]
 __refcount_dec_and_test include/linux/refcount.h:315 [inline]
 refcount_dec_and_test include/linux/refcount.h:333 [inline]
 io_put_req fs/io_uring.c:2140 [inline]
 io_queue_linked_timeout fs/io_uring.c:6300 [inline]
 __io_queue_sqe+0xbef/0xec0 fs/io_uring.c:6354
 io_submit_sqe fs/io_uring.c:6534 [inline]
 io_submit_sqes+0x2bbd/0x7c50 fs/io_uring.c:6660
 __do_sys_io_uring_enter fs/io_uring.c:9240 [inline]
 __se_sys_io_uring_enter+0x256/0x1d60 fs/io_uring.c:9182

io_link_timeout_fn() should put only one reference of the linked timeout
request, however in case of racing with the master request's completion
first io_req_complete() puts one and then io_put_req_deferred() is
called.

## References
- https://git.kernel.org/stable/c/ff4a96ba5c8f9b266706280ff8021d2ef3f17e86
- https://git.kernel.org/stable/c/0b2a990e5d2f76d020cb840c456e6ec5f0c27530
- https://git.kernel.org/stable/c/6f5d7a45f58d3abe3a936de1441b8d6318f978ff
- https://git.kernel.org/stable/c/876808dba2ff7509bdd7f230c4f374a0caf4f410
- https://git.kernel.org/stable/c/a298232ee6b9a1d5d732aa497ff8be0d45b5bd82
