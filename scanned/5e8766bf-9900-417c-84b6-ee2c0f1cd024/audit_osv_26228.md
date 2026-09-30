# [M] netfilter: nf_tables: fix memleak when more than 255 elements expired

## Summary
Severity: Medium
Advisory: CVE-2023-52581
Ecosystem: Linux
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-02
Source: https://osv.dev/vulnerability/CVE-2023-52581
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.5.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: fix memleak when more than 255 elements expired

When more than 255 elements expired we're supposed to switch to a new gc
container structure.

This never happens: u8 type will wrap before reaching the boundary
and nft_trans_gc_space() always returns true.

This means we recycle the initial gc container structure and
lose track of the elements that came before.

While at it, don't deref 'gc' after we've passed it to call_rcu.

## References
- https://git.kernel.org/stable/c/09c85f2d21ab6b5acba31a037985b13e8e6565b8
- https://git.kernel.org/stable/c/4aea243b6853d06c1d160a9955b759189aa02b14
- https://git.kernel.org/stable/c/7cf055b43756b10aa2b851c927c940f5ed652125
- https://git.kernel.org/stable/c/7e5d732e6902eb6a37b35480796838a145ae5f07
- https://git.kernel.org/stable/c/a995a68e8a3b48533e47c856865d109a1f1a9d01
- https://git.kernel.org/stable/c/cf5000a7787cbc10341091d37245a42c119d26c5
- https://git.kernel.org/stable/c/ef99506eaf1dc31feff1adfcfd68bc5535a22171
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52581.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
