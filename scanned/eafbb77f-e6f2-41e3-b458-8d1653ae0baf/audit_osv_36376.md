# [H] perf: Fix __perf_event_overflow() vs perf_remove_from_context() race

## Summary
Severity: High
Advisory: CVE-2026-23271
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-23271
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Fix __perf_event_overflow() vs perf_remove_from_context() race

Make sure that __perf_event_overflow() runs with IRQs disabled for all
possible callchains. Specifically the software events can end up running
it with only preemption disabled.

This opens up a race vs perf_event_exit_event() and friends that will go
and free various things the overflow path expects to be present, like
the BPF program.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/3f89b61dd504c5b6711de9759e053b082f9abf12
- https://git.kernel.org/stable/c/4df1a45819e50993cb351682a6ae8e7ed2d233a0
- https://git.kernel.org/stable/c/4f8d5812337871227bb2c98669a87c306a2f86ef
- https://git.kernel.org/stable/c/5c48fdc4b4623533d86e279f51531a7ba212eb87
- https://git.kernel.org/stable/c/bb190628fe5f2a73ba762a9972ba16c5e895f73e
- https://git.kernel.org/stable/c/c9bc1753b3cc41d0e01fbca7f035258b5f4db0ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23271.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
