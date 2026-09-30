# [H] mmc: loongson2: Fix sg iteration in data reorder functions

## Summary
Severity: High
Advisory: CVE-2026-80748
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80748
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mmc: loongson2: Fix sg iteration in data reorder functions

In ls2k0500_mmc_reorder_cmd_data() and ls2k2000_mmc_reorder_cmd_data(),
the for_each_sg() macro already iterates over the scatterlist entries,
with 'sg' pointing to the current entry. However, the code incorrectly
uses '&sg[i]' and 'sg_dma_len(&sg[i])' inside the loop, which treats
'sg' as an array base and indexes it again, leading to access of
wrong sg entries (or out-of-bounds if the list is not an array).

## References
- https://git.kernel.org/stable/c/00179ed9fbe07799676e2cb63c4e7f0e7cd80a5c
- https://git.kernel.org/stable/c/8f7f7a6d5aed8f346a1c936fba02033c73a337dc
- https://git.kernel.org/stable/c/db368164383c46f256ed8152a41ae9300e615028
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80748.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
