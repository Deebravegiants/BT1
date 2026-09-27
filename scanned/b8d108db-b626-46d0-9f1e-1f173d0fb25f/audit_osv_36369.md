# [H] net/sched: act_gate: snapshot parameters with RCU on replace

## Summary
Severity: High
Advisory: CVE-2026-23245
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2026-23245
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.253, >=5.11.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.18, >=6.19.0 <6.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_gate: snapshot parameters with RCU on replace

The gate action can be replaced while the hrtimer callback or dump path is
walking the schedule list.

Convert the parameters to an RCU-protected snapshot and swap updates under
tcf_lock, freeing the previous snapshot via call_rcu(). When REPLACE omits
the entry list, preserve the existing schedule so the effective state is
unchanged.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/035d0d09d5ab3ed3e93d18cde2b562a6719eea23
- https://git.kernel.org/stable/c/04d75529dc0f9be78786162ebab7424af4644df2
- https://git.kernel.org/stable/c/58b162e318d0243ad2d7d92456c0873f2494c351
- https://git.kernel.org/stable/c/62413a9c3cb183afb9bb6e94dd68caf4e4145f4c
- https://git.kernel.org/stable/c/8b1251bbf0f10ac745ed74bad4d3b433caa1eeae
- https://git.kernel.org/stable/c/dfc314d7c767e350f78a46a8f8b134f80e8ad432
- https://git.kernel.org/stable/c/fc98fd8d214693be91253d9a88cdf8e5e143d124
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23245.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23245
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
