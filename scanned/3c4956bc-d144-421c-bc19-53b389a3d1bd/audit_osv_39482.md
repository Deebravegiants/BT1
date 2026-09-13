# [H] iommu/vt-d: Flush cache for PASID table before using it

## Summary
Severity: High
Advisory: CVE-2026-45862
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45862
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.3.0 <6.12.75, >=6.7.0 <6.18.14, >=6.13.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Flush cache for PASID table before using it

When writing the address of a freshly allocated zero-initialized PASID
table to a PASID directory entry, do that after the CPU cache flush for
this PASID table, not before it, to avoid the time window when this
PASID table may be already used by non-coherent IOMMU hardware while
its contents in RAM is still some random old data, not zero-initialized.

## References
- https://git.kernel.org/stable/c/0616137b70e6d9a547d4b60df8e1b64e36d83661
- https://git.kernel.org/stable/c/22d169bdd2849fe6bd18c2643742e1c02be6451c
- https://git.kernel.org/stable/c/36244dfd3853f7bf89d03b8e90d56b23ce7fbc16
- https://git.kernel.org/stable/c/36990407cdd257473607e33802d00e978af2759e
- https://git.kernel.org/stable/c/5962c30a6f05ea1ab73f039e235bb30716243517
- https://git.kernel.org/stable/c/c93f23375d8c410954b0df825e814b632fd62b9d
- https://git.kernel.org/stable/c/cd75e77125c8a51754ca4cd60b4ca083ed735d1d
- https://git.kernel.org/stable/c/d15cda135148ea7ba929cfdbcf208182bc29a7aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45862.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
