# [H] net: smc: fix splice entry lifetime imbalance in smc_rx_splice

## Summary
Severity: High
Advisory: CVE-2026-74631
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74631
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: smc: fix splice entry lifetime imbalance in smc_rx_splice

smc_rx_splice() passes pages to splice_to_pipe() before taking the
references that cover the lifetime of each splice entry. In the
VM-backed RMB path, splice_to_pipe() may drop unqueued entries through
smc_rx_spd_release(), while queued entries are released later via the
pipe buffer callback.

The old post-splice accounting also derives the number of queued VM pages
from an offset mutated while building the descriptor, and a multi-page
splice pairs one sock_hold() with multiple sock_put() calls.

Take the page and socket references for every candidate entry before
splice_to_pipe(), and drop the matching private state, page reference,
and socket reference from smc_rx_spd_release() for entries that never
get queued. This fixes a refcount imbalance that can underflow page
refcounts and trigger a use-after-free.

## References
- https://git.kernel.org/stable/c/07ad246529d136d5ef441d5ab4c305d132ff3090
- https://git.kernel.org/stable/c/0b7d54cedea5cb158e21925ae0c6c2f5c87ed2a0
- https://git.kernel.org/stable/c/4515c78f4d9fd577270f012efeb062ea58b3682d
- https://git.kernel.org/stable/c/5d9686af2976741bbd79b150d1c9e60b81e7f12e
- https://git.kernel.org/stable/c/7ddc7af2ae7fc5a0c0635b245c0824c8b76de5cb
- https://git.kernel.org/stable/c/af02c67ce654356c58db20a0bb2db33ace3b07a8
- https://git.kernel.org/stable/c/c841789e456ec6751342fa800639ce8e82ff0e6b
- https://git.kernel.org/stable/c/ca8342b5fc24c249fdb998468f6a168b457c67e5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74631.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74631
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
