# [H] ksmbd: fix null pointer dereference in compare_guid_key()

## Summary
Severity: High
Advisory: CVE-2026-64141
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64141
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.142, >=6.7.0 <6.12.92, >=6.9.0 <6.18.34, >=6.13.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix null pointer dereference in compare_guid_key()

session_fd_check() walks the per-inode m_op_list during durable-handle
session teardown and sets op->conn = NULL for every opinfo whose conn
matched the closing session's connection. The matching opinfo, however,
stays linked in its per-ClientGuid lease_table_list entry's lb->lease_list
because destroy_lease_table() only runs on full TCP-connection teardown,
not on SESSION_LOGOFF.

If the same TCP connection then negotiates a fresh session with the
same ClientGuid (ClientGuid is bound to NEGOTIATE, not the session, and
is unchanged across LOGOFF + SETUP) and issues a SMB2 CREATE with a
lease context on a different inode, find_same_lease_key() walks
lb->lease_list, reaches the stale opinfo, and calls compare_guid_key(),
which unconditionally dereferences opinfo->conn->ClientGUID. The conn
pointer is NULL and the kernel panics.

Reproducer requires only a successful SMB2 SESSION_SETUP and a share
configured with 'durable handles = yes'. KASAN report on mainline
70390501d194:

  general protection fault, probably for non-canonical address
  0xdffffc0000000069: 0000 [#1] SMP KASAN PTI
  KASAN: null-ptr-deref in range [0x0000000000000348-0x000000000000034f]
  Workqueue: ksmbd-io handle_ksmbd_work
  RIP: 0010:bcmp+0x5b/0x230
  Call Trace:
   compare_guid_key+0x4b/0xd0
   find_same_lease_key+0x324/0x690
   smb2_open+0x6aea/0x8e60
   handle_ksmbd_work+0x796/0xee0
   ...

Faulting address 0x348 is the offset of ClientGUID within struct
ksmbd_conn, confirming opinfo->conn was NULL.

Read opinfo->conn once and bail out if it has been cleared by a
concurrent session_fd_check(). A half-detached opinfo cannot be the
owner of an active lease, so returning 0 is the correct match result.

## References
- https://git.kernel.org/stable/c/0836081b394ca074d1b910f2b990ff7b4b4404c7
- https://git.kernel.org/stable/c/4b83cbc4c15f09b000cc06f033f64b0824b6dc87
- https://git.kernel.org/stable/c/af86896ca3239e25a6bd7d352213371265073d38
- https://git.kernel.org/stable/c/cd5c1b75d2f454f625d7dc55bd3ae21d0855f6ad
- https://git.kernel.org/stable/c/e43cb36d4d7827710cfcd48e95e29a507f0d87be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64141.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64141
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
