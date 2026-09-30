# [H] l2tp: prevent possible tunnel refcount underflow

## Summary
Severity: High
Advisory: CVE-2024-49940
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49940
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

l2tp: prevent possible tunnel refcount underflow

When a session is created, it sets a backpointer to its tunnel. When
the session refcount drops to 0, l2tp_session_free drops the tunnel
refcount if session->tunnel is non-NULL. However, session->tunnel is
set in l2tp_session_create, before the tunnel refcount is incremented
by l2tp_session_register, which leaves a small window where
session->tunnel is non-NULL when the tunnel refcount hasn't been
bumped.

Moving the assignment to l2tp_session_register is trivial but
l2tp_session_create calls l2tp_session_set_header_len which uses
session->tunnel to get the tunnel's encap. Add an encap arg to
l2tp_session_set_header_len to avoid using session->tunnel.

If l2tpv3 sessions have colliding IDs, it is possible for
l2tp_v3_session_get to race with l2tp_session_register and fetch a
session which doesn't yet have session->tunnel set. Add a check for
this case.

## References
- https://git.kernel.org/stable/c/24256415d18695b46da06c93135f5b51c548b950
- https://git.kernel.org/stable/c/f7415e60c25a6108cd7955a20b2e66b6251ffe02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49940.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49940
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
