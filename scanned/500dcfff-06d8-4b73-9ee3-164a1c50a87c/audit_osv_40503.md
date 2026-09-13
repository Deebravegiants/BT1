# [H] ksmbd: reject non-VALID session in compound request branch

## Summary
Severity: High
Advisory: CVE-2026-53383
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53383
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.4.0 <6.12.95, >=6.7.0 <6.18.37, >=6.13.0 <7.0.14, >=6.19.0 <7.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: reject non-VALID session in compound request branch

smb2_check_user_session() takes a shortcut for any operation that is not
the first in a COMPOUND request: it reuses work->sess (the session bound by
the first operation) and validates only the SessionId, then returns
"valid". It never re-checks work->sess->state == SMB2_SESSION_VALID, and a
SessionId of 0xFFFFFFFFFFFFFFFF (ULLONG_MAX, the MS-SMB2 related-operation
value) skips even the id comparison. The standalone path
(ksmbd_session_lookup_all() plus the SESSION_SETUP state machine) does
enforce the VALID state; the compound branch bypasses all of it.

A SESSION_SETUP carrying only an NTLM Type-1 (NtLmNegotiate) blob publishes
a fresh SMB2_SESSION_IN_PROGRESS session whose sess->user is still NULL
(->user is assigned later, by ntlm_authenticate()). Used as operation 1 of
a COMPOUND with operation 2 = TREE_CONNECT (related, SessionId=ULLONG_MAX,
\\host\IPC$), the tree-connect then runs on that IN_PROGRESS session and
reaches ksmbd_ipc_tree_connect_request(), which dereferences
user_name(sess->user) with sess->user == NULL (transport_ipc.c:687/701/704)
-> remote NULL-pointer dereference and a kernel Oops that wedges the ksmbd
worker for all clients.

Reject any non-first compound operation that lands on a session which is
not SMB2_SESSION_VALID, mirroring the validity the standalone lookup path
enforces. SESSION_SETUP itself legitimately runs on an IN_PROGRESS session,
but it is never carried as a non-first compound operation, so multi-leg
authentication is unaffected by this check.

## References
- https://git.kernel.org/stable/c/06e1f05a1dbe8bbd054c0927b17fc0a61cc8bef7
- https://git.kernel.org/stable/c/25ff12b82a376ff5c4583102a63d2456a6b9ebb9
- https://git.kernel.org/stable/c/5f983b864d3d473ac533b2f4f44a1bbe5dcbccf4
- https://git.kernel.org/stable/c/609ca17d869d04ba249e32cdcbf13c0b1c66f43c
- https://git.kernel.org/stable/c/7cad3ceaf679c55bc9946685dacafce78ce6b51a
- https://git.kernel.org/stable/c/8f0302fb691537d33ec8f668565257ea9d340ffe
- https://git.kernel.org/stable/c/d2bbbb6c55812220fee5d801c275cc267ea3cbeb
- https://git.kernel.org/stable/c/fc578523a72cb8b329d32070b95898e81613cc3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
