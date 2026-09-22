# [M] netfilter: nft_set_rbtree: fix overlap expiration walk

## Summary
Severity: Medium
Advisory: CVE-2023-53304
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53304
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.190, >=5.11.0 <5.15.124, >=5.16.0 <6.1.43, >=6.2.0 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_rbtree: fix overlap expiration walk

The lazy gc on insert that should remove timed-out entries fails to release
the other half of the interval, if any.

Can be reproduced with tests/shell/testcases/sets/0044interval_overlap_0
in nftables.git and kmemleak enabled kernel.

Second bug is the use of rbe_prev vs. prev pointer.
If rbe_prev() returns NULL after at least one iteration, rbe_prev points
to element that is not an end interval, hence it should not be removed.

Lastly, check the genmask of the end interval if this is active in the
current generation.

## References
- https://git.kernel.org/stable/c/50cbb9d195c197af671869c8cadce3bd483735a0
- https://git.kernel.org/stable/c/8284a79136c384059e85e278da2210b809730287
- https://git.kernel.org/stable/c/893cb3c3513cf661a0ff45fe0cfa83fe27131f76
- https://git.kernel.org/stable/c/89a4d1a89751a0fbd520e64091873e19cc0979e8
- https://git.kernel.org/stable/c/acaee227cf79c45a5d2d49c3e9a66333a462802c
- https://git.kernel.org/stable/c/cd66733932399475fe933cb3ec03e687ed401462
- https://git.kernel.org/stable/c/f718863aca469a109895cb855e6b81fff4827d71
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53304.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
