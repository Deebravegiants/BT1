# [H] fs: afs: revert mmap_prepare() change

## Summary
Severity: High
Advisory: CVE-2026-46100
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46100
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs: afs: revert mmap_prepare() change

Partially reverts commit 9d5403b1036c ("fs: convert most other
generic_file_*mmap() users to .mmap_prepare()").

This is because the .mmap invocation establishes a refcount, but
.mmap_prepare is called at a point where a merge or an allocation failure
might happen after the call, which would leak the refcount increment.

Functionality is being added to permit the use of .mmap_prepare in this
case, but in the interim, we need to fix this.

## References
- https://git.kernel.org/stable/c/48c7a0eaeea41da17d1d84d2d7a4c40be122b246
- https://git.kernel.org/stable/c/f51f85c044809fbd39ac8ae07ac99bc43ce32bd5
- https://git.kernel.org/stable/c/fbfc6578eaca12daa0c09df1e9ba7f2c657b49da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46100
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
