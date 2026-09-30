# [C] rxrpc: fix RESPONSE authenticator parser OOB read

## Summary
Severity: Critical
Advisory: CVE-2026-31636
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31636
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: fix RESPONSE authenticator parser OOB read

rxgk_verify_authenticator() copies auth_len bytes into a temporary
buffer and then passes p + auth_len as the parser limit to
rxgk_do_verify_authenticator(). Since p is a __be32 *, that inflates the
parser end pointer by a factor of four and lets malformed RESPONSE
authenticators read past the kmalloc() buffer.

Decoded from the original latest-net reproduction logs with
scripts/decode_stacktrace.sh:

BUG: KASAN: slab-out-of-bounds in rxgk_verify_response()
Call Trace:
 dump_stack_lvl() [lib/dump_stack.c:123]
 print_report() [mm/kasan/report.c:379 mm/kasan/report.c:482]
 kasan_report() [mm/kasan/report.c:597]
 rxgk_verify_response()
   [net/rxrpc/rxgk.c:1103 net/rxrpc/rxgk.c:1167
    net/rxrpc/rxgk.c:1274]
 rxrpc_process_connection()
   [net/rxrpc/conn_event.c:266 net/rxrpc/conn_event.c:364
    net/rxrpc/conn_event.c:386]
 process_one_work() [kernel/workqueue.c:3281]
 worker_thread()
   [kernel/workqueue.c:3353 kernel/workqueue.c:3440]
 kthread() [kernel/kthread.c:436]
 ret_from_fork() [arch/x86/kernel/process.c:164]

Allocated by task 54:
 rxgk_verify_response()
   [include/linux/slab.h:954 net/rxrpc/rxgk.c:1155
    net/rxrpc/rxgk.c:1274]
 rxrpc_process_connection()
   [net/rxrpc/conn_event.c:266 net/rxrpc/conn_event.c:364
    net/rxrpc/conn_event.c:386]

Convert the byte count to __be32 units before constructing the parser
limit.

## References
- https://git.kernel.org/stable/c/20a188775a9a9982d1987e12660d9b44b40a6c99
- https://git.kernel.org/stable/c/3e3138007887504ee9206d0bfb5acb062c600025
- https://git.kernel.org/stable/c/7875f3d9777bd4e9892c4db830571ab8ac2044c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31636.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31636
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
