# [M] cifs: Fix xid leak in cifs_create()

## Summary
Severity: Medium
Advisory: CVE-2022-50351
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50351
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.76, >=5.16.0 <6.0.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix xid leak in cifs_create()

If the cifs already shutdown, we should free the xid before return,
otherwise, the xid will be leaked.

## References
- https://git.kernel.org/stable/c/593d877c39aa9f3fe1a4b5b022492886d7d700ec
- https://git.kernel.org/stable/c/92aa09c86ef297976a3c27c6574c0839418dc2c4
- https://git.kernel.org/stable/c/fee0fb1f15054bb6a0ede452acb42da5bef4d587
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50351.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50351
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
