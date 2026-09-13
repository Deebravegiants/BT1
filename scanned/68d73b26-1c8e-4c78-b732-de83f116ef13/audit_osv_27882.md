# [H] net: stmmac: protect updates of 64-bit statistics counters

## Summary
Severity: High
Advisory: CVE-2024-26690
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26690
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: protect updates of 64-bit statistics counters

As explained by a comment in <linux/u64_stats_sync.h>, write side of struct
u64_stats_sync must ensure mutual exclusion, or one seqcount update could
be lost on 32-bit platforms, thus blocking readers forever. Such lockups
have been observed in real world after stmmac_xmit() on one CPU raced with
stmmac_napi_poll_tx() on another CPU.

To fix the issue without introducing a new lock, split the statics into
three parts:

1. fields updated only under the tx queue lock,
2. fields updated only during NAPI poll,
3. fields updated only from interrupt context,

Updates to fields in the first two groups are already serialized through
other locks. It is sufficient to split the existing struct u64_stats_sync
so that each group has its own.

Note that tx_set_ic_bit is updated from both contexts. Split this counter
so that each context gets its own, and calculate their sum to get the total
value in stmmac_get_ethtool_stats().

For the third group, multiple interrupts may be processed by different CPUs
at the same time, but interrupts on the same CPU will not nest. Move fields
from this group to a newly created per-cpu struct stmmac_pcpu_stats.

## References
- https://git.kernel.org/stable/c/38cc3c6dcc09dc3a1800b5ec22aef643ca11eab8
- https://git.kernel.org/stable/c/9680b2ab54ba8d72581100e8c45471306101836e
- https://git.kernel.org/stable/c/e6af0f082a4b87b99ad033003be2a904a1791b3f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26690.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26690
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
