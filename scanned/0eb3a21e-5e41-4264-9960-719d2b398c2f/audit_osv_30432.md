# [H] fs/ntfs3: Mark inode as bad as soon as error detected in mi_enum_attr()

## Summary
Severity: High
Advisory: CVE-2024-52560
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-52560
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Mark inode as bad as soon as error detected in mi_enum_attr()

Extended the `mi_enum_attr()` function interface with an additional
parameter, `struct ntfs_inode *ni`, to allow marking the inode
as bad as soon as an error is detected.

## References
- https://git.kernel.org/stable/c/2afd4d267e6dbaec8d3ccd4f5396cb84bc67aa2e
- https://git.kernel.org/stable/c/d9c699f2c4dc174940ffe8600b20c267897da155
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52560.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52560
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
