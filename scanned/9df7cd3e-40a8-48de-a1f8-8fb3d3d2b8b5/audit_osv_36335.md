# [H] net/sched: qfq: Use cl_is_active to determine whether class is active in qfq_rm_from_ag

## Summary
Severity: High
Advisory: CVE-2026-23105
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23105
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.249, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.122, >=6.7.0 <6.12.68, >=6.13.0 <6.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: qfq: Use cl_is_active to determine whether class is active in qfq_rm_from_ag

This is more of a preventive patch to make the code more consistent and
to prevent possible exploits that employ child qlen manipulations on qfq.
use cl_is_active instead of relying on the child qdisc's qlen to determine
class activation.

## References
- https://git.kernel.org/stable/c/77f1afd0bb4d5da95236f6114e6d0dfcde187ff6
- https://git.kernel.org/stable/c/93b8635974fb050c43d07e35e5edfe6e685ca28a
- https://git.kernel.org/stable/c/abd9fc26ea577561a5ef6241a1b058755ffdad0c
- https://git.kernel.org/stable/c/b8c24cf5268fb3bfb8d16324c3dbb985f698c835
- https://git.kernel.org/stable/c/d837fbee92453fbb829f950c8e7cf76207d73f33
- https://git.kernel.org/stable/c/f27047abf7cac1b6f90c3ad60de21ef9f717c26d
- https://git.kernel.org/stable/c/fac2c67bb2bb732eae4283e45fc338af7e08c254
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23105.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23105
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
