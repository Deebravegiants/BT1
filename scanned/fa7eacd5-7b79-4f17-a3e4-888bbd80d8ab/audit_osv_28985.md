# [H] drivers/perf: hisi: hns3: Fix out-of-bound access when valid event group

## Summary
Severity: High
Advisory: CVE-2024-38568
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38568
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers/perf: hisi: hns3: Fix out-of-bound access when valid event group

The perf tool allows users to create event groups through following
cmd [1], but the driver does not check whether the array index is out
of bounds when writing data to the event_group array. If the number of
events in an event_group is greater than HNS3_PMU_MAX_HW_EVENTS, the
memory write overflow of event_group array occurs.

Add array index check to fix the possible array out of bounds violation,
and return directly when write new events are written to array bounds.

There are 9 different events in an event_group.
[1] perf stat -e '{pmu/event1/, ... ,pmu/event9/}

## References
- https://git.kernel.org/stable/c/3669baf308308385a2ab391324abdde5682af5aa
- https://git.kernel.org/stable/c/81bdd60a3d1d3b05e6cc6674845afb1694dd3a0e
- https://git.kernel.org/stable/c/aa2d3d678895c8eedd003f1473f87d3f06fe6ec7
- https://git.kernel.org/stable/c/b5120d322763c15c978bc47beb3b6dff45624304
- https://git.kernel.org/stable/c/be1fa711e59c874d049f592aef1d4685bdd22bdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38568.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38568
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
