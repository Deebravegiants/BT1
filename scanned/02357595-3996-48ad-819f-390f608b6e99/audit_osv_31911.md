# [H] net_sched: Prevent creation of classes with TC_H_ROOT

## Summary
Severity: High
Advisory: CVE-2025-21971
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21971
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.132, >=6.2.0 <6.6.84, >=6.7.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net_sched: Prevent creation of classes with TC_H_ROOT

The function qdisc_tree_reduce_backlog() uses TC_H_ROOT as a termination
condition when traversing up the qdisc tree to update parent backlog
counters. However, if a class is created with classid TC_H_ROOT, the
traversal terminates prematurely at this class instead of reaching the
actual root qdisc, causing parent statistics to be incorrectly maintained.
In case of DRR, this could lead to a crash as reported by Mingi Cho.

Prevent the creation of any Qdisc class with classid TC_H_ROOT
(0xFFFFFFFF) across all qdisc types, as suggested by Jamal.

## References
- https://git.kernel.org/stable/c/003d92c91cdb5a64b25a9a74cb8543aac9a8bb48
- https://git.kernel.org/stable/c/0c3057a5a04d07120b3d0ec9c79568fceb9c921e
- https://git.kernel.org/stable/c/5c3ca9cb48b51bd72bf76b8b05e24f3cd53db5e7
- https://git.kernel.org/stable/c/78533c4a29ac3aeddce4b481770beaaa4f3bfb67
- https://git.kernel.org/stable/c/7a82fe67a9f4d7123d8e5ba8f0f0806c28695006
- https://git.kernel.org/stable/c/94edfdfb9505ab608e86599d1d1e38c83816fc1c
- https://git.kernel.org/stable/c/e05d9938b1b0ac40b6054cc5fa0ccbd9afd5ed4c
- https://git.kernel.org/stable/c/e5ee00607bbfc97ef1526ea95b6b2458ac9e7cb7
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21971.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
