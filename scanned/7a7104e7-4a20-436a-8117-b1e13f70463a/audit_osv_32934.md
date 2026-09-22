# [H] LoongArch: KVM: Check validity of "num_cpu" from user space

## Summary
Severity: High
Advisory: CVE-2025-38366
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38366
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Check validity of "num_cpu" from user space

The maximum supported cpu number is EIOINTC_ROUTE_MAX_VCPUS about
irqchip EIOINTC, here add validation about cpu number to avoid array
pointer overflow.

## References
- https://git.kernel.org/stable/c/a3293b4078ee93174f70f36d3ab7618554ce6ab6
- https://git.kernel.org/stable/c/cc8d5b209e09d3b52bca1ffe00045876842d96ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38366.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
