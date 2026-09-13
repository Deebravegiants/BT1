# [H] tracing: Add down_write(trace_event_sem) when adding trace event

## Summary
Severity: High
Advisory: CVE-2025-38539
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38539
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Add down_write(trace_event_sem) when adding trace event

When a module is loaded, it adds trace events defined by the module. It
may also need to modify the modules trace printk formats to replace enum
names with their values.

If two modules are loaded at the same time, the adding of the event to the
ftrace_events list can corrupt the walking of the list in the code that is
modifying the printk format strings and crash the kernel.

The addition of the event should take the trace_event_sem for write while
it adds the new event.

Also add a lockdep_assert_held() on that semaphore in
__trace_add_event_dirs() as it iterates the list.

## References
- https://git.kernel.org/stable/c/33e20747b47ddc03569b6bc27a2d6894c1428182
- https://git.kernel.org/stable/c/6bc94f20a4c304997288f9a45278c9d0c06987d3
- https://git.kernel.org/stable/c/70fecd519caad0c1741c3379d5348c9000a5b29d
- https://git.kernel.org/stable/c/7803b28c9aa8d8bd4e19ebcf5f0db9612b0f333b
- https://git.kernel.org/stable/c/b5e8acc14dcb314a9b61ff19dcd9fdd0d88f70df
- https://git.kernel.org/stable/c/ca60064ea03f14e06c763de018403cb56ba3207d
- https://git.kernel.org/stable/c/db45632479ceecb669612ed8dbce927e3c6279fc
- https://git.kernel.org/stable/c/e70f5ee4c8824736332351b703c46f9469ed7f6c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38539.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38539
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
