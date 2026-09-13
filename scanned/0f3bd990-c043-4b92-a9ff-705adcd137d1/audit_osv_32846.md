# [C] netfilter: nf_set_pipapo_avx2: fix initial map fill

## Summary
Severity: Critical
Advisory: CVE-2025-38120
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38120
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.11.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_set_pipapo_avx2: fix initial map fill

If the first field doesn't cover the entire start map, then we must zero
out the remainder, else we leak those bits into the next match round map.

The early fix was incomplete and did only fix up the generic C
implementation.

A followup patch adds a test case to nft_concat_range.sh.

## References
- https://git.kernel.org/stable/c/251496ce1728c9fd47bd2b20a7b21b20b9a020ca
- https://git.kernel.org/stable/c/39bab2d3517b5b50c609b4f8c66129bf619fffa0
- https://git.kernel.org/stable/c/8068e1e42b46518ce680dc6470bcd710efc3fa0a
- https://git.kernel.org/stable/c/8164d0efaf370c425dc69a1e8216940d09e7de0c
- https://git.kernel.org/stable/c/90bc7f5a244aadee4292b28098b7c98aadd4b3aa
- https://git.kernel.org/stable/c/b5ad58285f9217d68cd5ea2ad86ce254a3fe7c4d
- https://git.kernel.org/stable/c/ea77c397bff8b6d59f6d83dae1425b08f465e8b5
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38120.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
