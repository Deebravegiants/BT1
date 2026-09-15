# [H] ksmbd: validate session id and tree id in the compound request

## Summary
Severity: High
Advisory: CVE-2023-3866
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2023-3866
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.121, >=5.16.0 <6.1.36, >=6.2.0 <6.3.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: validate session id and tree id in the compound request

This patch validate session id and tree id in compound request.
If first operation in the compound is SMB2 ECHO request, ksmbd bypass
session and tree validation. So work->sess and work->tcon could be NULL.
If secound request in the compound access work->sess or tcon, It cause
NULL pointer dereferecing error.

## References
- https://git.kernel.org/stable/c/5005bcb4219156f1bf7587b185080ec1da08518e
- https://git.kernel.org/stable/c/854156d12caa9d36de1cf5f084591c7686cc8a9d
- https://git.kernel.org/stable/c/d1066c1b3663401cd23c0d6e60cdae750ce00c0f
- https://git.kernel.org/stable/c/eb947403518ea3d93f6d89264bb1f5416bb0c7d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3866.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
