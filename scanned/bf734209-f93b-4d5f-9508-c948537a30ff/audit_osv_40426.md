# [H] RDMA/core: Validate cpu_id against nr_cpu_ids in DMAH alloc

## Summary
Severity: High
Advisory: CVE-2026-53187
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53187
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Validate cpu_id against nr_cpu_ids in DMAH alloc

The cpu_id attribute supplied by user space through
UVERBS_ATTR_ALLOC_DMAH_CPU_ID is passed directly to cpumask_test_cpu()
without first verifying that the value is within the valid CPU range.

Passing such untrusted data to cpumask_test_cpu() may lead to an
out-of-bounds read of the underlying cpumask bitmap: the helper expands
to a test_bit() that indexes the bitmap by cpu_id / BITS_PER_LONG with
no bound check.

In addition, on kernels built with CONFIG_DEBUG_PER_CPU_MAPS it trips
the WARN_ON_ONCE() in cpumask_check(); combined with panic_on_warn this
turns a bad user input into a machine reboot.

Reject any cpu_id that is not smaller than nr_cpu_ids with -EINVAL
before it is used.

Reported by Smatch.

## References
- https://git.kernel.org/stable/c/0efbb6b54ff56300867027d8e0800d0e32226a20
- https://git.kernel.org/stable/c/323c98a4ff06aa28114f2bf658fb43eb3b536bbc
- https://git.kernel.org/stable/c/bd5e818be7964c1689fba2dad9e6bd3a827fee74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53187.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
