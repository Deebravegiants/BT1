# [H] netfilter: nft_set_pipapo: split gc into unlink and reclaim phase

## Summary
Severity: High
Advisory: CVE-2026-23351
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23351
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_pipapo: split gc into unlink and reclaim phase

Yiming Qian reports Use-after-free in the pipapo set type:
  Under a large number of expired elements, commit-time GC can run for a very
  long time in a non-preemptible context, triggering soft lockup warnings and
  RCU stall reports (local denial of service).

We must split GC in an unlink and a reclaim phase.

We cannot queue elements for freeing until pointers have been swapped.
Expired elements are still exposed to both the packet path and userspace
dumpers via the live copy of the data structure.

call_rcu() does not protect us: dump operations or element lookups starting
after call_rcu has fired can still observe the free'd element, unless the
commit phase has made enough progress to swap the clone and live pointers
before any new reader has picked up the old version.

This a similar approach as done recently for the rbtree backend in commit
35f83a75529a ("netfilter: nft_set_rbtree: don't gc elements on insert").

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/16f3595c0441d87dfa005c47d8f95be213afaa9e
- https://git.kernel.org/stable/c/500a50a301ce962b019ab95053ac70264fec2c21
- https://git.kernel.org/stable/c/65ca51b9fb85477ab92a04295aed34b38f7c062e
- https://git.kernel.org/stable/c/7864c667aed01a58b87ca518a631322cd0ac34c0
- https://git.kernel.org/stable/c/9df95785d3d8302f7c066050117b04cd3c2048c2
- https://git.kernel.org/stable/c/aff13667708dfa0dce136b8efd81baa9fa6ef261
- https://git.kernel.org/stable/c/c0f1f85097ac2b6e7d750fe4d05807985cd3fd3a
- https://git.kernel.org/stable/c/c12d570d71920903a1a0468b7d13b085203d0c93
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23351.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23351
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
