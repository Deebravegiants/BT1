# [H] netfilter: nft_set_rbtree: skip sync GC for new elements in this transaction

## Summary
Severity: High
Advisory: CVE-2023-52433
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2023-52433
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_set_rbtree: skip sync GC for new elements in this transaction

New elements in this transaction might expired before such transaction
ends. Skip sync GC for such elements otherwise commit path might walk
over an already released object. Once transaction is finished, async GC
will collect such expired element.

## References
- https://git.kernel.org/stable/c/03caf75da1059f0460666c826e9f50e13dfd0017
- https://git.kernel.org/stable/c/2ee52ae94baabf7ee09cf2a8d854b990dac5d0e4
- https://git.kernel.org/stable/c/9a8c544158f68f656d1734eb5ba00c4f817b76b1
- https://git.kernel.org/stable/c/9af7dfb3c9d7985172a240f85e684c5cd33e29ce
- https://git.kernel.org/stable/c/9db9feb841f7449772f9393c16b9ef4536d8c127
- https://git.kernel.org/stable/c/c323ed65f66e5387ee0a73452118d49f1dae81b8
- https://git.kernel.org/stable/c/e3213ff99a355cda811b41e8dbb3472d13167a3a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52433.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52433
- https://security.netapp.com/advisory/ntap-20240828-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
