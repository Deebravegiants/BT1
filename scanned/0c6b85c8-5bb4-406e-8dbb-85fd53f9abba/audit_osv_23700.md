# [M] netfilter: nf_tables: memleak flow rule from commit path

## Summary
Severity: Medium
Advisory: CVE-2022-49358
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49358
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: memleak flow rule from commit path

Abort path release flow rule object, however, commit path does not.
Update code to destroy these objects before releasing the transaction.

## References
- https://git.kernel.org/stable/c/330c0c6cd2150a2d7f47af16aa590078b0d2f736
- https://git.kernel.org/stable/c/5b8d63489c3b701eb2a76f848ec94d8cbc9373b9
- https://git.kernel.org/stable/c/80de9ea1f5b808a6601e91111fae601df2b26369
- https://git.kernel.org/stable/c/9dd732e0bdf538b1b76dc7c157e2b5e560ff30d3
- https://git.kernel.org/stable/c/ab9f34a30c23f656e76f4c5b83125a4e7b53c86e
- https://git.kernel.org/stable/c/e33d9bd563e71f6c6528b96008d65524a459c4dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49358.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49358
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
