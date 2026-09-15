# [C] smb: server: fix use-after-free in smb2_open()

## Summary
Severity: Critical
Advisory: CVE-2026-43378
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43378
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: server: fix use-after-free in smb2_open()

The opinfo pointer obtained via rcu_dereference(fp->f_opinfo) is
dereferenced after rcu_read_unlock(), creating a use-after-free
window.

## References
- https://git.kernel.org/stable/c/190e5f808e8058640b408ccfed25440b441a718a
- https://git.kernel.org/stable/c/1e689a56173827669a35da7cb2a3c78ed5c53680
- https://git.kernel.org/stable/c/54b48ae83de8bb06e65079d96368efe359d4909c
- https://git.kernel.org/stable/c/8f5b1a7cb009a93c48e9e334a2f59a660f9afc07
- https://git.kernel.org/stable/c/b720c84087cb547f23ce03eab93568c1769e4556
- https://git.kernel.org/stable/c/e1b21e6066615e7d3d3a7aa2677e415e563fd7cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43378.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
