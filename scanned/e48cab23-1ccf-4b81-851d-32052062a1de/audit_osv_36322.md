# [H] net/sched: sch_qfq: do not free existing class in qfq_change_class()

## Summary
Severity: High
Advisory: CVE-2026-22999
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-25
Source: https://osv.dev/vulnerability/CVE-2026-22999
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.67, >=6.13.0 <6.18.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_qfq: do not free existing class in qfq_change_class()

Fixes qfq_change_class() error case.

cl->qdisc and cl should only be freed if a new class and qdisc
were allocated, or we risk various UAF.

## References
- https://git.kernel.org/stable/c/0a234660dc70ce45d771cbc76b20d925b73ec160
- https://git.kernel.org/stable/c/2a64fb9b47afffeb5dbab5fd3a518e1436dcc90e
- https://git.kernel.org/stable/c/362e269bb03f7076ba9990e518aeddb898232e50
- https://git.kernel.org/stable/c/3879cffd9d07aa0377c4b8835c4f64b4fb24ac78
- https://git.kernel.org/stable/c/cff6cd703f41d8071995956142729e4bba160363
- https://git.kernel.org/stable/c/e9d8f11652fa08c647bf7bba7dd8163241a332cd
- https://git.kernel.org/stable/c/f06f7635499bc806cbe2bbc8805c7cef8b1edddf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22999
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
