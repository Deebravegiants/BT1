# [M] firmware: stratix10-svc: Fix a potential resource leak in svc_create_memory_pool()

## Summary
Severity: Medium
Advisory: CVE-2023-53255
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53255
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware: stratix10-svc: Fix a potential resource leak in svc_create_memory_pool()

svc_create_memory_pool() is only called from stratix10_svc_drv_probe().
Most of resources in the probe are managed, but not this memremap() call.

There is also no memunmap() call in the file.

So switch to devm_memremap() to avoid a resource leak.

## References
- https://git.kernel.org/stable/c/1995f15590ca222f91193ed11461862b450abfd6
- https://git.kernel.org/stable/c/7363de081c793e47866cb54ce7cb8a480cffc259
- https://git.kernel.org/stable/c/974ac045a05ad12a0b4578fb303f00dcc22f3aba
- https://git.kernel.org/stable/c/c04ed61ebf01968d7699b121663982493ed577fb
- https://git.kernel.org/stable/c/cb8a31a56df8492fb0d900959238e1a3ff8b8981
- https://git.kernel.org/stable/c/e3373e6b6c79aff698442b00d20c9f285d296e46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53255.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53255
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
