# [H] l2tp: pppol2tp: hold reference to session in pppol2tp_ioctl()

## Summary
Severity: High
Advisory: CVE-2026-53262
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53262
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

l2tp: pppol2tp: hold reference to session in pppol2tp_ioctl()

pppol2tp_ioctl() read sock->sk->sk_user_data directly without any
locks or reference counting.  If a controllable sleep was induced during
copy_from_user() (e.g. via a userfaultfd page fault sleep), a concurrent
socket close could trigger pppol2tp_session_close() asynchronously.  This
frees the l2tp_session structure via the l2tp_session_del_work workqueue.
Upon resuming, the ioctl thread dereferences the stale session pointer,
resulting in a Use-After-Free (UAF).

Fix this by securely fetching the session reference using the RCU-safe,
refcounted helper pppol2tp_sock_to_session(sk) on entry.  This locks the
session's refcount across the sleep.  We structured the function to exit
via standard err breaks, guaranteeing that l2tp_session_put() is cleanly
called on all return paths to drop the reference.

To preserve existing behavior we validate the session and its magic
signature only for the specific L2TP commands that require it.  This
ensures that generic/unknown ioctls called on an unconnected socket
still return -ENOIOCTLCMD and correctly fall back to generic handlers
(e.g. in sock_do_ioctl()).

## References
- https://git.kernel.org/stable/c/62f327e287cf7b595ae3f73ba72f5cd2a9e9f39f
- https://git.kernel.org/stable/c/78cdfdca88cbf731a92f3b9ee5427c633dd94e28
- https://git.kernel.org/stable/c/a213a8950414c684999dcf03edeea6c46ede172e
- https://git.kernel.org/stable/c/e251d4cdfc725c9e7d686161e3b775a0e7d95053
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
