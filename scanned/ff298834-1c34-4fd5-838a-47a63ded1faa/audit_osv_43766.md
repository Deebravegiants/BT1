# [H] net/sched: sch_cake: drop WARN_ON(1) for malformed packets in ACK filter

## Summary
Severity: High
Advisory: CVE-2026-74704
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74704
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: sch_cake: drop WARN_ON(1) for malformed packets in ACK filter

The sch_cake ACK filter parses packets to find the TCP header and filter
duplicated ACKs if the flow is backlogged. The parsing code contains a
WARN_ON(1) which can be triggered by a malformed IP header in certain
cases. Depending on the system configuration, this leads either to
either spamming dmesg with warnings, or a panic if panic_on_warn is set.

The code already correctly skips the offending packet in the branch that
triggers the warning, so the WARN_ON itself doesn't really serve any
purpose. So just drop it altogether to avoid the inconvenient side
effects.

## References
- https://git.kernel.org/stable/c/0c4882bff34558d8d53fb04c3e96da5c327c7dc8
- https://git.kernel.org/stable/c/2504a76e5c0694e14e15562730e1339f2d9f9458
- https://git.kernel.org/stable/c/2a33516f9ef59ad11844d4fc152f889449b5daf3
- https://git.kernel.org/stable/c/a1ae353d8355407c1bea971d1c1af5e7f242bb7d
- https://git.kernel.org/stable/c/a4b52612004a5639c4bfc30ba93ba414b8326e2a
- https://git.kernel.org/stable/c/ae1b2f8e21a41e7c7e75511bea0c4ccc59ec1bd3
- https://git.kernel.org/stable/c/c1693b7844a6c06d31a565e5a494948034dfd235
- https://git.kernel.org/stable/c/cd2f1d9fe8a507c2dc86ad326fe221f121c47734
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74704.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74704
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
