# [C] ksmbd: fix use-after-free in kerberos authentication

## Summary
Severity: Critical
Advisory: CVE-2025-37924
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37924
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.138, >=6.2.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in kerberos authentication

Setting sess->user = NULL was introduced to fix the dangling pointer
created by ksmbd_free_user. However, it is possible another thread could
be operating on the session and make use of sess->user after it has been
passed to ksmbd_free_user but before sess->user is set to NULL.

## References
- https://git.kernel.org/stable/c/28c756738af44a404a91b77830d017bb0c525890
- https://git.kernel.org/stable/c/b447463562238428503cfba1c913261047772f90
- https://git.kernel.org/stable/c/e18c616718018dfc440e4a2d2b94e28fe91b1861
- https://git.kernel.org/stable/c/e34a33d5d7e87399af0a138bb32f6a3e95dd83d2
- https://git.kernel.org/stable/c/e86e9134e1d1c90a960dd57f59ce574d27b9a124
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37924.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37924
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
