# [H] ntfs3: Add bounds checking to mi_enum_attr()

## Summary
Severity: High
Advisory: CVE-2024-50248
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50248
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.120, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs3: Add bounds checking to mi_enum_attr()

Added bounds checking to make sure that every attr don't stray beyond
valid memory region.

## References
- https://git.kernel.org/stable/c/22cdf3be7d34f61a91b9e2966fec3a29f3871398
- https://git.kernel.org/stable/c/386613a44b858304a88529ade2ccc1e079a5fc56
- https://git.kernel.org/stable/c/556bdf27c2dd5c74a9caacbe524b943a6cd42d99
- https://git.kernel.org/stable/c/809f9b419c75f8042c58434d2bfe849140643e9d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50248.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
