# [H] tracing: Delay module ref count for "enable_event" trigger

## Summary
Severity: High
Advisory: CVE-2026-68177
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68177
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Delay module ref count for "enable_event" trigger

Triggers are now delayed from freeing, but can still be triggered until
after the RCU grace period has ended. The freeing of the enable_event data
is put into the private_data_free() callback, but the put of the module
refcount is done immediately.

It is possible that if a module is removed that has an event that would
enable (or disable) it is still active, it can read the data of the module
after it is removed causing a use-after-free bug.

Move the trace_event_put_ref() that releases the module into the delayed
callback so that the module can not be removed until any reference to its
events are finished.

## References
- https://git.kernel.org/stable/c/159fdc3e01dca5fdbc412fcd8b239895733a270d
- https://git.kernel.org/stable/c/e091351b38818ef620d27f44f4bfd625f13afbff
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68177.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68177
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
