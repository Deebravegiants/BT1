# [M] soc: ti: ti_sci_pm_domains: Check for null return of devm_kcalloc

## Summary
Severity: Medium
Advisory: CVE-2022-49453
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49453
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: ti: ti_sci_pm_domains: Check for null return of devm_kcalloc

The allocation funciton devm_kcalloc may fail and return a null pointer,
which would cause a null-pointer dereference later.
It might be better to check it and directly return -ENOMEM just like the
usage of devm_kcalloc in previous code.

## References
- https://git.kernel.org/stable/c/01ba41a359622ab256ce4d4f8b94c67165ae3daf
- https://git.kernel.org/stable/c/05efc4591f80582b6fe53366b70b6a35a42fd255
- https://git.kernel.org/stable/c/7cef9274fa1b8506949d74bc45aef072b890824a
- https://git.kernel.org/stable/c/ba56291e297d28aa6eb82c5c1964fae2d7594746
- https://git.kernel.org/stable/c/c4e188869406b47ac3350920bf165be303cb1c96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49453.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
