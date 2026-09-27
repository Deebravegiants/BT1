# [H] ksmbd: fix use-after-free in smb2_lock

## Summary
Severity: High
Advisory: CVE-2025-21945
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21945
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in smb2_lock

If smb_lock->zero_len has value, ->llist of smb_lock is not delete and
flock is old one. It will cause use-after-free on error handling
routine.

## References
- https://git.kernel.org/stable/c/410ce35a2ed6d0e114132bba29af49b69880c8c7
- https://git.kernel.org/stable/c/636e021646cf9b52ddfea7c809b018e91f2188cb
- https://git.kernel.org/stable/c/84d2d1641b71dec326e8736a749b7ee76a9599fc
- https://git.kernel.org/stable/c/8573571060ca466cbef2c6f03306b2cc7b883506
- https://git.kernel.org/stable/c/a0609097fd10d618aed4864038393dd75131289e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21945.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21945
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
