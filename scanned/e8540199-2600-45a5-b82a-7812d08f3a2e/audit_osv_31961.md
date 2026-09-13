# [H] ksmbd: fix use-after-free in ksmbd_sessions_deregister()

## Summary
Severity: High
Advisory: CVE-2025-22041
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22041
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in ksmbd_sessions_deregister()

In multichannel mode, UAF issue can occur in session_deregister
when the second channel sets up a session through the connection of
the first channel. session that is freed through the global session
table can be accessed again through ->sessions of connection.

## References
- https://git.kernel.org/stable/c/15a9605f8d69dc85005b1a00c31a050b8625e1aa
- https://git.kernel.org/stable/c/33cc29e221df7a3085ae413e8c26c4e81a151153
- https://git.kernel.org/stable/c/8ed0e9d2f410f63525afb8351181eea36c80bcf1
- https://git.kernel.org/stable/c/a8a8ae303a8395cbac270b5b404d85df6ec788f8
- https://git.kernel.org/stable/c/ca042cc0e4f9e0d2c8f86dd67e4b22f30a516a9b
- https://git.kernel.org/stable/c/f0eb3f575138b816da74697bd506682574742fcd
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22041.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
