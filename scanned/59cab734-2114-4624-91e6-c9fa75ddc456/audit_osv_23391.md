# [M] powerpc/pseries: Fix potential memleak in papr_get_attr()

## Summary
Severity: Medium
Advisory: CVE-2022-48669
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2022-48669
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/pseries: Fix potential memleak in papr_get_attr()

`buf` is allocated in papr_get_attr(), and krealloc() of `buf`
could fail. We need to free the original `buf` in the case of failure.

## References
- https://git.kernel.org/stable/c/1699fb915b9f61794d559b55114c09a390aaf234
- https://git.kernel.org/stable/c/7f7d39fe3d80d6143404940b2413010cf6527029
- https://git.kernel.org/stable/c/a3f22feb2220a945d1c3282e34199e8bcdc5afc4
- https://git.kernel.org/stable/c/cda9c0d556283e2d4adaa9960b2dc19b16156bae
- https://git.kernel.org/stable/c/d0647c3e81eff62b66d46fd4e475318cb8cb3610
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48669.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
