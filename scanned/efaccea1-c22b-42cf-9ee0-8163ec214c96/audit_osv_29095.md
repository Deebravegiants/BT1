# [H] netfilter: ipset: Fix race between namespace cleanup and gc in the list:set type

## Summary
Severity: High
Advisory: CVE-2024-39503
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-39503
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: Fix race between namespace cleanup and gc in the list:set type

Lion Ackermann reported that there is a race condition between namespace cleanup
in ipset and the garbage collection of the list:set type. The namespace
cleanup can destroy the list:set type of sets while the gc of the set type is
waiting to run in rcu cleanup. The latter uses data from the destroyed set which
thus leads use after free. The patch contains the following parts:

- When destroying all sets, first remove the garbage collectors, then wait
  if needed and then destroy the sets.
- Fix the badly ordered "wait then remove gc" for the destroy a single set
  case.
- Fix the missing rcu locking in the list:set type in the userspace test
  case.
- Use proper RCU list handlings in the list:set type.

The patch depends on c1193d9bbbd3 (netfilter: ipset: Add list flush to cancel_gc).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/0f1bb77c6d837c9513943bc7c08f04c5cc5c6568
- https://git.kernel.org/stable/c/2ba35b37f780c6410bb4bba9c3072596d8576702
- https://git.kernel.org/stable/c/390b353d1a1da3e9c6c0fd14fe650d69063c95d6
- https://git.kernel.org/stable/c/4e7aaa6b82d63e8ddcbfb56b4fd3d014ca586f10
- https://git.kernel.org/stable/c/90ae20d47de602198eb69e6cd7a3db3420abfc08
- https://git.kernel.org/stable/c/93b53c202b51a69e42ca57f5a183f7e008e19f83
- https://git.kernel.org/stable/c/c0761d1f1ce1d5b85b5e82bbb714df12de1aa8c3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39503.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-39503
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
