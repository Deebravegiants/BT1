# [H] ocfs2: strict bound check before memcmp in ocfs2_xattr_find_entry()

## Summary
Severity: High
Advisory: CVE-2024-41016
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41016
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.112, >=6.2.0 <6.6.53, >=6.7.0 <6.10.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ocfs2: strict bound check before memcmp in ocfs2_xattr_find_entry()

xattr in ocfs2 maybe 'non-indexed', which saved with additional space
requested.  It's better to check if the memory is out of bound before
memcmp, although this possibility mainly comes from crafted poisonous
images.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/57a3d89831fcaa2cdbe024b47c7c36d5a56c3637
- https://git.kernel.org/stable/c/af77c4fc1871847b528d58b7fdafb4aa1f6a9262
- https://git.kernel.org/stable/c/c031d286eceb82f72f8623b7f4abd2aa491bfb5e
- https://git.kernel.org/stable/c/c726dea9d0c806d64c26fcef483b1fb9474d8c5e
- https://git.kernel.org/stable/c/cfb926051fab19b10d1e65976211f364aa820180
- https://git.kernel.org/stable/c/e2b3d7a9d019d4d1a0da6c3ea64a1ff79c99c090
- https://git.kernel.org/stable/c/e4ffea01adf3323c821b6f37e9577d2d400adbaa
- https://git.kernel.org/stable/c/e8f9c4af7af7e9e4cd09c0251c7936593147419f
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41016.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
