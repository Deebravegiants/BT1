# [M] reset: uniphier-glue: Fix possible null-ptr-deref

## Summary
Severity: Medium
Advisory: CVE-2022-49758
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49758
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

reset: uniphier-glue: Fix possible null-ptr-deref

It will cause null-ptr-deref when resource_size(res) invoked,
if platform_get_resource() returns NULL.

## References
- https://git.kernel.org/stable/c/3a2390c6777e3f6662980c6cfc25cafe9e4fef98
- https://git.kernel.org/stable/c/633bad3dc81ce2aa561f704ec091e49eb647bd0b
- https://git.kernel.org/stable/c/95de286200b2a046da01c4aeba02ae9220d68ca4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49758.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49758
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
