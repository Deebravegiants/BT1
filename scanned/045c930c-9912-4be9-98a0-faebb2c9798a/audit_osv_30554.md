# [H] exfat: fix out-of-bounds access of directory entries

## Summary
Severity: High
Advisory: CVE-2024-53147
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53147
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

exfat: fix out-of-bounds access of directory entries

In the case of the directory size is greater than or equal to
the cluster size, if start_clu becomes an EOF cluster(an invalid
cluster) due to file system corruption, then the directory entry
where ei->hint_femp.eidx hint is outside the directory, resulting
in an out-of-bounds access, which may cause further file system
corruption.

This commit adds a check for start_clu, if it is an invalid cluster,
the file or directory will be treated as empty.

## References
- https://git.kernel.org/stable/c/184fa506e392eb78364d9283c961217ff2c0617b
- https://git.kernel.org/stable/c/3ddd1cb2b458ff6a193bc845f408dfff217db29e
- https://git.kernel.org/stable/c/a0120d6463368378539ef928cf067d02372efb8c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53147.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53147
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
