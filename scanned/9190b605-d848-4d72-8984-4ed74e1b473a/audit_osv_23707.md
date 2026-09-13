# [H] net: ethernet: mtk_eth_soc: out of bounds read in mtk_hwlro_get_fdir_entry()

## Summary
Severity: High
Advisory: CVE-2022-49368
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49368
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_eth_soc: out of bounds read in mtk_hwlro_get_fdir_entry()

The "fsp->location" variable comes from user via ethtool_get_rxnfc().
Check that it is valid to prevent an out of bounds read.

## References
- https://git.kernel.org/stable/c/0b238f75b65ed4462ef4cdfa718cac0ac7fce3b8
- https://git.kernel.org/stable/c/2bd1faedb74dc2a2be3972abcd4239b75a3e7b00
- https://git.kernel.org/stable/c/4cde554c70d7397cfa2e4116bacb4accdfb6fd48
- https://git.kernel.org/stable/c/5ba81f82607ead85fe36f50869fc4f5661359ab8
- https://git.kernel.org/stable/c/657e7174603f0aab2cdedc64ac81edffd2a87afe
- https://git.kernel.org/stable/c/71ae30662ec610b92644d13f79c78f76f17873b3
- https://git.kernel.org/stable/c/b24ca1cf846273361d5bd73a35de95a486a54b6d
- https://git.kernel.org/stable/c/b4f0e57ea0d867aacffad7999527e48bd4ea9293
- https://git.kernel.org/stable/c/e7e7104e2d5ddf3806a28695670f21bef471f1e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49368.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
