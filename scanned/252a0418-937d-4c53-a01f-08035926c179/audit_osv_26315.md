# [H] wifi: ath12k: fix possible out-of-bound read in ath12k_htt_pull_ppdu_stats()

## Summary
Severity: High
Advisory: CVE-2023-52827
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52827
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix possible out-of-bound read in ath12k_htt_pull_ppdu_stats()

len is extracted from HTT message and could be an unexpected value in
case errors happen, so add validation before using to avoid possible
out-of-bound read in the following message iteration and parsing.

The same issue also applies to ppdu_info->ppdu_stats.common.num_users,
so validate it before using too.

These are found during code review.

Compile test only.

## References
- https://git.kernel.org/stable/c/1bc44a505a229bb1dd4957e11aa594edeea3690e
- https://git.kernel.org/stable/c/79527c21a3ce04cffc35ea54f74ee087e532be57
- https://git.kernel.org/stable/c/c9e44111da221246efb2e623ae1be40a5cf6542c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52827.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52827
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
