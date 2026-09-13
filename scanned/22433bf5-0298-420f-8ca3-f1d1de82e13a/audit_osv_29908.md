# [H] ocfs2: add bounds checking to ocfs2_xattr_find_entry()

## Summary
Severity: High
Advisory: CVE-2024-47670
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-47670
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.112, >=6.2.0 <6.6.53, >=6.7.0 <6.10.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: add bounds checking to ocfs2_xattr_find_entry()

Add a paranoia check to make sure it doesn't stray beyond valid memory
region containing ocfs2 xattr entries when scanning for a match.  It will
prevent out-of-bound access in case of crafted images.

## References
- https://git.kernel.org/stable/c/1f6e167d6753fe3ea493cdc7f7de8d03147a4d39
- https://git.kernel.org/stable/c/34759b7e4493d7337cbc414c132cef378c492a2c
- https://git.kernel.org/stable/c/5bbe51eaf01a5dd6fb3f0dea81791e5dbc6dc6dd
- https://git.kernel.org/stable/c/60c0d36189bad58b1a8e69af8781d90009559ea1
- https://git.kernel.org/stable/c/8e7bef408261746c160853fc27df3139659f5f77
- https://git.kernel.org/stable/c/9b32539590a8e6400ac2f6e7cf9cbb8e08711a2f
- https://git.kernel.org/stable/c/9e3041fecdc8f78a5900c3aa51d3d756e73264d6
- https://git.kernel.org/stable/c/b49a786beb11ff740cb9e0c20b999c2a0e1729c2
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47670.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47670
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
