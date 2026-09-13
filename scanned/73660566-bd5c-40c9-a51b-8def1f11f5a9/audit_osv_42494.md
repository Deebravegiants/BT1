# [H] rds: tcp: unregister sysctl before tearing down listen socket

## Summary
Severity: High
Advisory: CVE-2026-68290
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68290
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.101, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rds: tcp: unregister sysctl before tearing down listen socket

rds_tcp_exit_net() frees the per-netns RDS TCP listen socket via
rds_tcp_kill_sock() before unregistering the per-netns sysctl table.  Since
rds_tcp_skbuf_handler() derives the netns from
rtn->rds_tcp_listen_sock->sk, a concurrent sysctl write can race with
netns teardown and dereference the freed socket/sk.

KASAN reports the race as:

  BUG: KASAN: slab-use-after-free in rds_tcp_skbuf_handler+0x2aa/0x2e0
  rds_tcp_skbuf_handler              net/rds/tcp.c:721
  proc_sys_call_handler              fs/proc/proc_sysctl.c
  vfs_write                          fs/read_write.c
  __x64_sys_pwrite64                 fs/read_write.c

Fix this by unregistering the RDS TCP sysctl table before calling
rds_tcp_kill_sock().  unregister_net_sysctl_table() prevents new sysctl
handlers from starting and waits for in-flight handlers to finish, so
the listen socket can then be released safely. The fix was tested
against the linked reproducer.

## References
- https://git.kernel.org/stable/c/167e54c703ccd4fa028feb568b0d1002020cff86
- https://git.kernel.org/stable/c/16df2d154ec82e2f7e7585b4fa154751ba37729a
- https://git.kernel.org/stable/c/3aa13fe0c1bb7bc5312f878e61523e5d8cf3f85d
- https://git.kernel.org/stable/c/80fffed08dc1c10e971066941d2daa56253f1552
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68290.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
