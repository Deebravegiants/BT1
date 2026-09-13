# [H] net_sched: sch_sfq: reject invalid perturb period

## Summary
Severity: High
Advisory: CVE-2025-38193
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-04
Source: https://osv.dev/vulnerability/CVE-2025-38193
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.297, >=5.5.0 <5.10.240, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: sch_sfq: reject invalid perturb period

Gerrard Tai reported that SFQ perturb_period has no range check yet,
and this can be used to trigger a race condition fixed in a separate patch.

We want to make sure ctl->perturb_period * HZ will not overflow
and is positive.


tc qd add dev lo root sfq perturb -10   # negative value : error
Error: sch_sfq: invalid perturb period.

tc qd add dev lo root sfq perturb 1000000000 # too big : error
Error: sch_sfq: invalid perturb period.

tc qd add dev lo root sfq perturb 2000000 # acceptable value
tc -s -d qd sh dev lo
qdisc sfq 8005: root refcnt 2 limit 127p quantum 64Kb depth 127 flows 128 divisor 1024 perturb 2000000sec
 Sent 0 bytes 0 pkt (dropped 0, overlimits 0 requeues 0)
 backlog 0b 0p requeues 0

## References
- https://git.kernel.org/stable/c/0357da9149eac621f39e235a135ebf155f01f7c3
- https://git.kernel.org/stable/c/2254d038dab9c194fe6a4b1ce31034f42e91a6e5
- https://git.kernel.org/stable/c/590b2d7d0beadba2aa576708a05a05f0aae39295
- https://git.kernel.org/stable/c/7ca52541c05c832d32b112274f81a985101f9ba8
- https://git.kernel.org/stable/c/956b5aebb349449b38d920d444ca1392d43719d1
- https://git.kernel.org/stable/c/b11a50544af691b787384089b68f740ae20a441b
- https://git.kernel.org/stable/c/e0936ff56be4e08ad5b60ec26971eae0c40af305
- https://git.kernel.org/stable/c/f9b97d466e6026ccbdda30bb5b71965b67ccbc82
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38193.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38193
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
