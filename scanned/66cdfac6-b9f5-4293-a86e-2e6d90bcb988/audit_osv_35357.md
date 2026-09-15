# [H] ksmbd: Fix refcount leak when invalid session is found on session lookup

## Summary
Severity: High
Advisory: CVE-2025-71150
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2025-71150
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Fix refcount leak when invalid session is found on session lookup

When a session is found but its state is not SMB2_SESSION_VALID, It
indicates that no valid session was found, but it is missing to decrement
the reference count acquired by the session lookup, which results in
a reference count leak. This patch fixes the issue by explicitly calling
ksmbd_user_session_put to release the reference to the session.

## References
- https://git.kernel.org/stable/c/02e06785e85b4bd86ef3d23b7c8d87acc76773d5
- https://git.kernel.org/stable/c/0fb87b28cafae71e9c8248432cc3a6a1fd759efc
- https://git.kernel.org/stable/c/11fe566b442e3bc2774191740fd377739a87a1c0
- https://git.kernel.org/stable/c/8cabcb4dd3dc85dd83a37d26efcc59a66a4074d7
- https://git.kernel.org/stable/c/cafb57f7bdd57abba87725eb4e82bbdca4959644
- https://git.kernel.org/stable/c/e54fb2a4772545701766cba08aab20de5eace8cd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71150.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
