# [H] CVE-2021-47368

## Summary
Severity: High
Advisory: CVE-2021-47368
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47368
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

enetc: Fix illegal access when reading affinity_hint

irq_set_affinity_hit() stores a reference to the cpumask_t
parameter in the irq descriptor, and that reference can be
accessed later from irq_affinity_hint_proc_show(). Since
the cpu_mask parameter passed to irq_set_affinity_hit() has
only temporary storage (it's on the stack memory), later
accesses to it are illegal. Thus reads from the corresponding
procfs affinity_hint file can result in paging request oops.

The issue is fixed by the get_cpu_mask() helper, which provides
a permanent storage for the cpumask_t parameter.

## References
- https://git.kernel.org/stable/c/6c3f1b741c6c2914ea120e3a5790d3e900152f7b
- https://git.kernel.org/stable/c/6f329d9da2a5ae032fcde800a99b118124ed5270
- https://git.kernel.org/stable/c/7237a494decfa17d0b9d0076e6cee3235719de90
- https://git.kernel.org/stable/c/4c4c3052911b577920353a7646e4883d5da40c28
