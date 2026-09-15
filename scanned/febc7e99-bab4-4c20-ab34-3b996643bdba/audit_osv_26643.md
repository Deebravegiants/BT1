# [M] mfd: arizona: Use pm_runtime_resume_and_get() to prevent refcnt leak

## Summary
Severity: Medium
Advisory: CVE-2023-53443
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53443
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mfd: arizona: Use pm_runtime_resume_and_get() to prevent refcnt leak

In arizona_clk32k_enable(), we should use pm_runtime_resume_and_get()
as pm_runtime_get_sync() will increase the refcnt even when it
returns an error.

## References
- https://git.kernel.org/stable/c/4414a7ab80cebf715045e3c4d465feefbad21139
- https://git.kernel.org/stable/c/5a47bb71b1a94a279144fc3031d3c4591b38dd16
- https://git.kernel.org/stable/c/7195e642b49af60d4120fa1b45bd812ba528174f
- https://git.kernel.org/stable/c/754e81ff44061dda68da0fd4ef51bd1aa9fbf2cf
- https://git.kernel.org/stable/c/9893771097b22a8743a446e45994a177795ca4da
- https://git.kernel.org/stable/c/dc9437e9889c3dacf1f320e3cf08da74127573fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53443.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53443
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
