# [H] remoteproc: mtk_scp: Fix a potential double free

## Summary
Severity: High
Advisory: CVE-2022-49391
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49391
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

remoteproc: mtk_scp: Fix a potential double free

'scp->rproc' is allocated using devm_rproc_alloc(), so there is no need
to free it explicitly in the remove function.

## References
- https://git.kernel.org/stable/c/adc02700236613b344a947a897fc2741d52a43b9
- https://git.kernel.org/stable/c/eac3e5b1c12f85732e60f5f8b985444d273866bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49391.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
