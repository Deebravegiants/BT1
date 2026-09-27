# [H] tracing: Check return value of __register_event() in trace_module_add_events()

## Summary
Severity: High
Advisory: CVE-2026-74471
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74471
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Check return value of __register_event() in trace_module_add_events()

trace_module_add_events() ignores the return value of __register_event()
and unconditionally calls __add_event_to_tracers() for each event.

If __register_event() fails (for example, if event_init() fails), the
trace_event_call is not added to ftrace_events list, but
__add_event_to_tracers() still creates a trace_event_file pointing to it.
If module loading subsequently fails and module memory is freed, tracing
state retains a stale trace_event_call pointer in trace_event_file,
leading to a use-after-free when tracefs or tracing subsystem operations
are later executed.

Fix this by checking the return value of __register_event() and only
calling __add_event_to_tracers() if event registration succeeded.

## References
- https://git.kernel.org/stable/c/000765dcdc3edf128990762790543adc4b868f6c
- https://git.kernel.org/stable/c/22f954f7a8afe975e85517aff41b35defe05144b
- https://git.kernel.org/stable/c/3bf965a2827c44f03294107703e7ba53fbd0a69a
- https://git.kernel.org/stable/c/54b7a358f6399c1242d2fb7f4f96085af34baa5e
- https://git.kernel.org/stable/c/9d6d79744f01eacaf3d5522f4fcd59939581abfd
- https://git.kernel.org/stable/c/ac8719969e6c3c54e939834df812bc41f25453cf
- https://git.kernel.org/stable/c/cbb5ed3be9cae70e1c12b1991009b4e12bf4a4ca
- https://git.kernel.org/stable/c/d61ee2a27dfd5eb43ddc18af40168f5b9eb1cea5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74471.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74471
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
