# [H] powerpc/perf: Fix ref-counting on the PMU 'vpa_pmu'

## Summary
Severity: High
Advisory: CVE-2025-22094
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22094
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/perf: Fix ref-counting on the PMU 'vpa_pmu'

Commit 176cda0619b6 ("powerpc/perf: Add perf interface to expose vpa
counters") introduced 'vpa_pmu' to expose Book3s-HV nested APIv2 provided
L1<->L2 context switch latency counters to L1 user-space via
perf-events. However the newly introduced PMU named 'vpa_pmu' doesn't
assign ownership of the PMU to the module 'vpa_pmu'. Consequently the
module 'vpa_pmu' can be unloaded while one of the perf-events are still
active, which can lead to kernel oops and panic of the form below on a
Pseries-LPAR:

BUG: Kernel NULL pointer dereference on read at 0x00000058
<snip>
 NIP [c000000000506cb8] event_sched_out+0x40/0x258
 LR [c00000000050e8a4] __perf_remove_from_context+0x7c/0x2b0
 Call Trace:
 [c00000025fc3fc30] [c00000025f8457a8] 0xc00000025f8457a8 (unreliable)
 [c00000025fc3fc80] [fffffffffffffee0] 0xfffffffffffffee0
 [c00000025fc3fcd0] [c000000000501e70] event_function+0xa8/0x120
<snip>
 Kernel panic - not syncing: Aiee, killing interrupt handler!

Fix this by adding the module ownership to 'vpa_pmu' so that the module
'vpa_pmu' is ref-counted and prevented from being unloaded when perf-events
are initialized.

## References
- https://git.kernel.org/stable/c/6cf045b51e2c5721db7e55305f09ee32741e00f9
- https://git.kernel.org/stable/c/70ea7c5189197c6f5acdcfd8a2651be2c41e2faa
- https://git.kernel.org/stable/c/ff99d5b6a246715f2257123cdf6c4a29cb33aa78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22094.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
