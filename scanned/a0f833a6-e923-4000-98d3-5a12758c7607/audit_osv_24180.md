# [H] staging: vme_user: Fix possible UAF in tsi148_dma_list_add

## Summary
Severity: High
Advisory: CVE-2022-50384
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50384
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vme_user: Fix possible UAF in tsi148_dma_list_add

Smatch report warning as follows:

drivers/staging/vme_user/vme_tsi148.c:1757 tsi148_dma_list_add() warn:
  '&entry->list' not removed from list

In tsi148_dma_list_add(), the error path "goto err_dma" will not
remove entry->list from list->entries, but entry will be freed,
then list traversal may cause UAF.

Fix by removeing it from list->entries before free().

## References
- https://git.kernel.org/stable/c/1f5661388f43df3ac106ce93e67d8d22b16a78ff
- https://git.kernel.org/stable/c/357057ee55d3c99a5de5abe8150f7bca04f8e53b
- https://git.kernel.org/stable/c/51c0ad3b7c5b01f9314758335a13f157b05fa56d
- https://git.kernel.org/stable/c/5cc4eea715a3fcf4e516662f736dfee63979465f
- https://git.kernel.org/stable/c/5d2b286eb034af114f67d9967fc3fbc1829bb712
- https://git.kernel.org/stable/c/85db68fc901da52314ded80aace99f8b684c7815
- https://git.kernel.org/stable/c/a45ba33d398a821147d7e5f16ead7eb125e331e2
- https://git.kernel.org/stable/c/cf138759a7e92c75cfc1b7ba705e4108fe330edf
- https://git.kernel.org/stable/c/e6b0adff99edf246ba1f8d464530a0438cb1cbda
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50384.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
