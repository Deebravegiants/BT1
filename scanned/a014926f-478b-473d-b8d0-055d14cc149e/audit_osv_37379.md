# [H] ext4: reject mount if bigalloc with s_first_data_block != 0

## Summary
Severity: High
Advisory: CVE-2026-31447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31447
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: reject mount if bigalloc with s_first_data_block != 0

bigalloc with s_first_data_block != 0 is not supported, reject mounting
it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3822743dc20386d9897e999dbb990befa3a5b3f8
- https://git.kernel.org/stable/c/3a926957cc95899ef88529710836edadc03c71a1
- https://git.kernel.org/stable/c/5ad6d994255e27a3254079dfb50ca861fc31f2d0
- https://git.kernel.org/stable/c/7b58c110b4e1f028eb38eec9ed3555e9be81c8b0
- https://git.kernel.org/stable/c/7d5b04290156c3fc316eecc86a4f9d201ab7d44a
- https://git.kernel.org/stable/c/ad1f6d608f33f59d21a3d025615d6786a6443998
- https://git.kernel.org/stable/c/b77de3fceafbb39f30e4ff5dc986f863d5456417
- https://git.kernel.org/stable/c/d787d3ae96648dc14a3b7ca8fde817177e82c1c7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
