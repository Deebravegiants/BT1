# [H] af_unix: read UNIX_DIAG_VFS data under unix_state_lock

## Summary
Severity: High
Advisory: CVE-2026-31673
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31673
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_unix: read UNIX_DIAG_VFS data under unix_state_lock

Exact UNIX diag lookups hold a reference to the socket, but not to
u->path. Meanwhile, unix_release_sock() clears u->path under
unix_state_lock() and drops the path reference after unlocking.

Read the inode and device numbers for UNIX_DIAG_VFS while holding
unix_state_lock(), then emit the netlink attribute after dropping the
lock.

This keeps the VFS data stable while the reply is being built.

## References
- https://git.kernel.org/stable/c/0c739f3785f84af695952c2bac8be2f45082c9b8
- https://git.kernel.org/stable/c/39897df386376912d561d4946499379effa1e7ef
- https://git.kernel.org/stable/c/4f6a8f10182c3a9d22e8eb183957ae7ade9e4bf7
- https://git.kernel.org/stable/c/900a4e0910e98b8caef117d5df00471fa438dcf9
- https://git.kernel.org/stable/c/b9232421a77a649c9376c99fdfc8cb7f79cad34c
- https://git.kernel.org/stable/c/bdf206e740bf2919d818f132c8c9cc7ed91d11c0
- https://git.kernel.org/stable/c/c3ec44ab4526bbc4b6c9fc845af86488244f4c9b
- https://git.kernel.org/stable/c/e7339db13b9ddb63417b12da55fd6191e59f7442
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31673.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31673
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
