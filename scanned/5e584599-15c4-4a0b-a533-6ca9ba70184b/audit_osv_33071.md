# [H] jfs: upper bound check of tree index in dbAllocAG

## Summary
Severity: High
Advisory: CVE-2025-38697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38697
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: upper bound check of tree index in dbAllocAG

When computing the tree index in dbAllocAG, we never check if we are
out of bounds realative to the size of the stree.
This could happen in a scenario where the filesystem metadata are
corrupted.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/1467a75819e41341cd5ebd16faa2af1ca3c8f4fe
- https://git.kernel.org/stable/c/173cfd741ad7073640bfb7e2344c2a0ee005e769
- https://git.kernel.org/stable/c/2dd05f09cc323018136a7ecdb3d1007be9ede27f
- https://git.kernel.org/stable/c/30e19a884c0b11f33821aacda7e72e914bec26ef
- https://git.kernel.org/stable/c/49ea46d9025aa1914b24ea957636cbe4367a7311
- https://git.kernel.org/stable/c/5bdb9553fb134fd52ec208a8b378120670f6e784
- https://git.kernel.org/stable/c/a4f199203f79ca9cd7355799ccb26800174ff093
- https://git.kernel.org/stable/c/c214006856ff52a8ff17ed8da52d50601d54f9ce
- https://git.kernel.org/stable/c/c8ca21a2836993d7cb816668458e05e598574e55
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38697.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
