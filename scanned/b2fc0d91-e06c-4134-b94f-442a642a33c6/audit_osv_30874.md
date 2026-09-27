# [M] bpf,perf: Fix invalid prog_array access in perf_event_detach_bpf_prog

## Summary
Severity: Medium
Advisory: CVE-2024-56665
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56665
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf,perf: Fix invalid prog_array access in perf_event_detach_bpf_prog

Syzbot reported [1] crash that happens for following tracing scenario:

  - create tracepoint perf event with attr.inherit=1, attach it to the
    process and set bpf program to it
  - attached process forks -> chid creates inherited event

    the new child event shares the parent's bpf program and tp_event
    (hence prog_array) which is global for tracepoint

  - exit both process and its child -> release both events
  - first perf_event_detach_bpf_prog call will release tp_event->prog_array
    and second perf_event_detach_bpf_prog will crash, because
    tp_event->prog_array is NULL

The fix makes sure the perf_event_detach_bpf_prog checks prog_array
is valid before it tries to remove the bpf program from it.

[1] https://lore.kernel.org/bpf/Z1MR6dCIKajNS6nU@krava/T/#m91dbf0688221ec7a7fc95e896a7ef9ff93b0b8ad

## References
- https://git.kernel.org/stable/c/842e5af282453983586e2eae3c8eaf252de5f22f
- https://git.kernel.org/stable/c/978c4486cca5c7b9253d3ab98a88c8e769cb9bbd
- https://git.kernel.org/stable/c/c2b6b47662d5f2dfce92e5ffbdcac8229f321d9d
- https://git.kernel.org/stable/c/dfb15ddf3b65e0df2129f9756d1b4fa78055cdb3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56665.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
