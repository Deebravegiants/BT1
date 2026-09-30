# [H] octeontx2-pf: avoid double free of pool->stack on AQ init failure

## Summary
Severity: High
Advisory: CVE-2026-64222
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64222
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-pf: avoid double free of pool->stack on AQ init failure

otx2_pool_aq_init() frees pool->stack when mailbox sync or retry
allocation fails, but leaves the pointer unchanged. Later,
otx2_sq_aura_pool_init() unwinds the partial setup through
otx2_aura_pool_free(), which frees pool->stack again. The CN20K-specific
cn20k_pool_aq_init() implementation has the same bug in
its corresponding error path.

Set pool->stack to NULL immediately after the local free so the shared
cleanup path does not free the same stack again while cleaning up
partially initialized pool state.

The bug was first flagged by an experimental analysis tool we are
developing for kernel memory-management bugs while analyzing
v6.13-rc1. The tool is still under development and is not yet publicly
available. Manual inspection confirms that the bug is still present in
v7.1-rc3.

Runtime validation was not performed because reproducing this path
requires OcteonTX2/CN20K hardware.

## References
- https://git.kernel.org/stable/c/0488a0bb344fb1992853b60082acff6be8164d74
- https://git.kernel.org/stable/c/0d9b9d7dbef976ae7f855b6358f1d703014e96ea
- https://git.kernel.org/stable/c/4c29603498b05c049dbbbc47e882f2fbf0193cd7
- https://git.kernel.org/stable/c/94192b0579333c3deee2441379aab8ca98fc2e6b
- https://git.kernel.org/stable/c/9b244c242bec48b37e82b89787afd6a4c43457e1
- https://git.kernel.org/stable/c/b92e7ea408b6f1144648909c9c49a55d245d7300
- https://git.kernel.org/stable/c/c4b8c5d51632538b19ee01cf6d70cbceeefbd3ec
- https://git.kernel.org/stable/c/e6e9bc0bf963662b7042048ab0281014625d4cb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64222.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
