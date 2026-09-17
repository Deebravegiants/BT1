# [H] ksmbd: track the connection owning a byte-range lock

## Summary
Severity: High
Advisory: CVE-2026-64390
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64390
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: track the connection owning a byte-range lock

SMB2_LOCK adds each granted byte-range lock to both the file lock list
and the lock list of the connection which handled the request.  The
final close and durable handle paths, however, remove the connection
list entry while holding fp->conn->llist_lock.

With SMB3 multichannel, the connection handling the LOCK request can be
different from the connection which opened the file.  The entry can
therefore be removed under a different spinlock from the one protecting
the list it belongs to.  A concurrent traversal can then access freed
struct ksmbd_lock and struct file_lock objects.

Record the connection owning each lock's clist entry and hold a
reference to it while the entry is linked.  Use that connection and its
llist_lock for unlock, rollback, close, and durable preserve.  Durable
reconnect assigns the new connection as the owner when publishing the
locks again.

## References
- https://git.kernel.org/stable/c/22d38cf75b556c20b039743bdf3654d535b858be
- https://git.kernel.org/stable/c/427faaa52b0b399940c1a88065a5c310d10dad15
- https://git.kernel.org/stable/c/5fecc15a30cb9ebd310f7b52c1ab607edcea78f6
- https://git.kernel.org/stable/c/66eb3643164e5e1029907793926c132f8b5c6148
- https://git.kernel.org/stable/c/c1016dd1d8b2bcd1158bbaabe94a31bb7e7431fb
- https://git.kernel.org/stable/c/ea5c9bf99f626a15cc59f645dc895f2b3f01992e
- https://git.kernel.org/stable/c/fe20d492a69a6f79e637f438072b212e21ed3b78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
