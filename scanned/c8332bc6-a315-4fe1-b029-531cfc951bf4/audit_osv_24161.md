# [M] i2c: mux: reg: check return value after calling platform_get_resource()

## Summary
Severity: Medium
Advisory: CVE-2022-50364
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50364
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

i2c: mux: reg: check return value after calling platform_get_resource()

It will cause null-ptr-deref in resource_size(), if platform_get_resource()
returns NULL, move calling resource_size() after devm_ioremap_resource() that
will check 'res' to avoid null-ptr-deref.
And use devm_platform_get_and_ioremap_resource() to simplify code.

## References
- https://git.kernel.org/stable/c/2d47b79d2bd39cc6369eccf94a06568d84c906ae
- https://git.kernel.org/stable/c/61df25c41b8e0d2c988ccf17139f70075a2e1ba4
- https://git.kernel.org/stable/c/8212800943997fab61874550278d653cb378c60c
- https://git.kernel.org/stable/c/f5049b3ad9446203b916ee375f30fa217735f63a
- https://git.kernel.org/stable/c/f7a440c89b6d460154efeb058272760e41bdfea8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50364.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
