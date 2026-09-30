# [H] rds: drop incoming messages that cross network namespace boundaries

## Summary
Severity: High
Advisory: CVE-2026-68335
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68335
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rds: drop incoming messages that cross network namespace boundaries

rds_find_bound() looks up the destination socket using a global
rhashtable keyed solely on (addr, port, scope_id).  Network namespaces
are not part of the key, so a sender in netns A can deliver an incoming
message (inc) to a socket that lives in a different netns B.

When this happens, inc->i_conn points to an rds_connection whose c_net
is netns A, but the receiving rs lives in netns B.  Once the child
process that created netns A exits, cleanup_net() calls
rds_loop_exit_net() -> rds_loop_kill_conns() -> rds_conn_destroy(),
freeing that connection.  If the survivor socket in netns B still holds
the inc, any subsequent dereference of inc->i_conn is a use-after-free.

There are two dangerous sites in rds_clear_recv_queue():
  1. inc->i_conn->c_lcong (offset 88 of freed rds_connection, size 200)
     read via rds_recv_rcvbuf_delta() -- confirmed by KASAN.
  2. inc->i_conn->c_trans->inc_free(inc) (function pointer at offset 80)
     called via rds_inc_put() when the inc refcount reaches zero -- same
     race window, potential call-through-freed-object primitive.

The bug is reachable from unprivileged user namespaces
(CLONE_NEWUSER + CLONE_NEWNET), available since Linux 3.8.

Fix this by rejecting the delivery in rds_recv_incoming() when the
socket returned by rds_find_bound() belongs to a different network
namespace than the connection that carried the message.  Use the
existing rds_conn_net() / sock_net() helpers and net_eq() for the
comparison.

## References
- https://git.kernel.org/stable/c/03c574112e5d066df0ddce36d7438e850bcf3050
- https://git.kernel.org/stable/c/0f8690e3869109cd5803ccb400889d20a0b54e0e
- https://git.kernel.org/stable/c/1e2e2d9806944fe485824d617c8b7c78116c22db
- https://git.kernel.org/stable/c/5521ae71e32a8069ed4ca6e792179dc57bc43ab2
- https://git.kernel.org/stable/c/742ff6f02545212e991cd8b45011e40d2c2ef25a
- https://git.kernel.org/stable/c/9591042533140dfe6608d9344806d567dcd39d02
- https://git.kernel.org/stable/c/abff41fd928328bbf3dda1140beb2e61fa424ccd
- https://git.kernel.org/stable/c/cfb3ce07b705e486e022a2f2b1242b48f13981ff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68335.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68335
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
