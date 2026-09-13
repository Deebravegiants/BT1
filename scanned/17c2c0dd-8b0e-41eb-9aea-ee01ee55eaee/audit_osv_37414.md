# [H] perf: Make sure to use pmu_ctx->pmu for groups

## Summary
Severity: High
Advisory: CVE-2026-31528
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31528
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Make sure to use pmu_ctx->pmu for groups

Oliver reported that x86_pmu_del() ended up doing an out-of-bound memory access
when group_sched_in() fails and needs to roll back.

This *should* be handled by the transaction callbacks, but he found that when
the group leader is a software event, the transaction handlers of the wrong PMU
are used. Despite the move_group case in perf_event_open() and group_sched_in()
using pmu_ctx->pmu.

Turns out, inherit uses event->pmu to clone the events, effectively undoing the
move_group case for all inherited contexts. Fix this by also making inherit use
pmu_ctx->pmu, ensuring all inherited counters end up in the same pmu context.

Similarly, __perf_event_read() should use equally use pmu_ctx->pmu for the
group case.

## References
- https://git.kernel.org/stable/c/35f7914e54fe7f13654c22ee045b05e4b6d8062b
- https://git.kernel.org/stable/c/3a696e84a8b1fafdd774bb30d62919faf844d9e4
- https://git.kernel.org/stable/c/4b9ce671960627b2505b3f64742544ae9801df97
- https://git.kernel.org/stable/c/4c759446046500a1a6785b25725725c3ff087ace
- https://git.kernel.org/stable/c/656f35b463995bee024d948440128230aacd81e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31528.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31528
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
