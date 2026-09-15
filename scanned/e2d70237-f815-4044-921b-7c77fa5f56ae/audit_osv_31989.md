# [H] fs/ntfs3: Fix a couple integer overflows on 32bit systems

## Summary
Severity: High
Advisory: CVE-2025-22081
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22081
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix a couple integer overflows on 32bit systems

On 32bit systems the "off + sizeof(struct NTFS_DE)" addition can
have an integer wrapping issue.  Fix it by using size_add().

## References
- https://git.kernel.org/stable/c/0538f52410b619737e663167b6a2b2d0bc1a589d
- https://git.kernel.org/stable/c/0922d86a7a6032cb1694eab0b44b861bd33ba8d5
- https://git.kernel.org/stable/c/0dfe700fbd3525f30a36ffbe390a5b9319bd009a
- https://git.kernel.org/stable/c/1a14e9718a19d2e88de004a1360bfd7a86ed1395
- https://git.kernel.org/stable/c/284c9549386e9883855fb82b730303bb2edea9de
- https://git.kernel.org/stable/c/4d0f4f42922a832388a0c2fe5204c0a1037ff786
- https://git.kernel.org/stable/c/5ad414f4df2294b28836b5b7b69787659d6aa708
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22081.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
