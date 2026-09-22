# [H] jfs: nlink overflow in jfs_rename

## Summary
Severity: High
Advisory: CVE-2025-71292
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2025-71292
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: nlink overflow in jfs_rename

If nlink is maximal for a directory (-1) and inside that directory you
perform a rename for some child directory (not moving from the parent),
then the nlink of the first directory is first incremented and later
decremented. Normally this is fine, but when nlink = -1 this causes a
wrap around to 0, and then drop_nlink issues a warning.

After applying the patch syzbot no longer issues any warnings. I also
ran some basic fs tests to look for any regressions.

## References
- https://git.kernel.org/stable/c/2108829a59f081e822fdab8c2cd7131deb8aa8a1
- https://git.kernel.org/stable/c/5d77c36cd4b698649f5c30c5f6c084f4f61d1880
- https://git.kernel.org/stable/c/9218dc26fd922b09858ecd3666ed57dfd8098da8
- https://git.kernel.org/stable/c/93c325746ae59709b4f9bad4e3e4761c8d566c70
- https://git.kernel.org/stable/c/a3d66089e50a6e0142f8884471f74292102ea9aa
- https://git.kernel.org/stable/c/b4330a0d0947fbdc9d445cbbeabd8cc910a8c9ca
- https://git.kernel.org/stable/c/f70fcbc2ac7c24f087a2c895c5753aa730b1e479
- https://git.kernel.org/stable/c/fe136426e30ca6debcf916fd6a141555ed9fde74
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71292.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71292
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
