# [C] net/mlx5e: Fix CT entry update leaks of modify header context

## Summary
Severity: Critical
Advisory: CVE-2024-43864
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-20
Source: https://osv.dev/vulnerability/CVE-2024-43864
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.45, >=6.7.0 <6.10.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5e: Fix CT entry update leaks of modify header context

The cited commit allocates a new modify header to replace the old
one when updating CT entry. But if failed to allocate a new one, eg.
exceed the max number firmware can support, modify header will be
an error pointer that will trigger a panic when deallocating it. And
the old modify header point is copied to old attr. When the old
attr is freed, the old modify header is lost.

Fix it by restoring the old attr to attr when failed to allocate a
new modify header context. So when the CT entry is freed, the right
modify header context will be freed. And the panic of accessing
error pointer is also fixed.

## References
- https://git.kernel.org/stable/c/025f2b85a5e5a46df14ecf162c3c80a957a36d0b
- https://git.kernel.org/stable/c/89064d09c56b44c668509bf793c410484f63f5ad
- https://git.kernel.org/stable/c/daab2cc17b6b6ab158566bba037e9551fd432b59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43864.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
