# [H] ksmbd: do not expire session on binding failure

## Summary
Severity: High
Advisory: CVE-2026-31476
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31476
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: do not expire session on binding failure

When a multichannel session binding request fails (e.g. wrong password),
the error path unconditionally sets sess->state = SMB2_SESSION_EXPIRED.
However, during binding, sess points to the target session looked up via
ksmbd_session_lookup_slowpath() -- which belongs to another connection's
user. This allows a remote attacker to invalidate any active session by
simply sending a binding request with a wrong password (DoS).

Fix this by skipping session expiration when the failed request was
a binding attempt, since the session does not belong to the current
connection. The reference taken by ksmbd_session_lookup_slowpath() is
still correctly released via ksmbd_user_session_put().

## References
- https://git.kernel.org/stable/c/1d1888b4a7aec518b707f6eca0bf08992c0e8da3
- https://git.kernel.org/stable/c/4642ea35c03cf3d3558c009df4757cdb7af3f82d
- https://git.kernel.org/stable/c/6fafc4c4238e538969f1375f9ecdc6587c53f1cc
- https://git.kernel.org/stable/c/9bbb19d21ded7d78645506f20d8c44895e3d0fb9
- https://git.kernel.org/stable/c/a897064a457056acb976e20e3007cdf553de340f
- https://git.kernel.org/stable/c/e0e5edc81b241c70355217de7e120c97c3429deb
- https://git.kernel.org/stable/c/f5300690c23c5ac860499bb37dbc09cf43fd62e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31476.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31476
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
