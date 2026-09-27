# [H] ksmbd: fix session use-after-free in multichannel connection

## Summary
Severity: High
Advisory: CVE-2025-22040
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22040
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix session use-after-free in multichannel connection

There is a race condition between session setup and
ksmbd_sessions_deregister. The session can be freed before the connection
is added to channel list of session.
This patch check reference count of session before freeing it.

## References
- https://git.kernel.org/stable/c/3980770cb1470054e6400fd97668665975726737
- https://git.kernel.org/stable/c/596407adb9af1ee75fe7c7529607783d31b66e7f
- https://git.kernel.org/stable/c/7dfbd4c43eed91dd2548a95236908025707a8dfd
- https://git.kernel.org/stable/c/9069939d762138e232a6f79e3e1462682ed6a17d
- https://git.kernel.org/stable/c/94c281721d4ed2d972232414b91d98a6f5bdb16b
- https://git.kernel.org/stable/c/fa4cdb8cbca7d6cb6aa13e4d8d83d1103f6345db
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22040.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22040
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
