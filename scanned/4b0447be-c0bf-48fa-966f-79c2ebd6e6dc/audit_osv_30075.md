# [H] ocfs2: remove unreasonable unlock in ocfs2_read_blocks

## Summary
Severity: High
Advisory: CVE-2024-49965
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49965
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.323, >=4.20.0 <5.10.227, >=5.5.0 <5.15.168, >=5.11.0 <6.1.113, >=5.16.0 <6.6.55, >=6.2.0 <6.10.14, >=6.7.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: remove unreasonable unlock in ocfs2_read_blocks

Patch series "Misc fixes for ocfs2_read_blocks", v5.

This series contains 2 fixes for ocfs2_read_blocks().  The first patch fix
the issue reported by syzbot, which detects bad unlock balance in
ocfs2_read_blocks().  The second patch fixes an issue reported by Heming
Zhao when reviewing above fix.


This patch (of 2):

There was a lock release before exiting, so remove the unreasonable unlock.

## References
- https://git.kernel.org/stable/c/39a88623af3f1c686bf6db1e677ed865ffe6fccc
- https://git.kernel.org/stable/c/3f1ca6ba5452d53c598a45d21267a2c0c221eef3
- https://git.kernel.org/stable/c/5245f109b4afb6595360d4c180d483a6d2009a59
- https://git.kernel.org/stable/c/81aba693b129e82e11bb54f569504d943d018de9
- https://git.kernel.org/stable/c/84543da867c967edffd5065fa910ebf56aaae49d
- https://git.kernel.org/stable/c/9753bcb17b36c9add9b32c61766ddf8d2d161911
- https://git.kernel.org/stable/c/c03a82b4a0c935774afa01fd6d128b444fd930a1
- https://git.kernel.org/stable/c/df4f20fc3673cee11abf2c571987a95733cb638d
- https://git.kernel.org/stable/c/f55a33fe0fb5274ef185fd61947cf142138958af
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49965.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49965
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
