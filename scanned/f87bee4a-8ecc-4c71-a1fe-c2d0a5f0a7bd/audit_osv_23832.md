# [M] fs/ntfs3: provide block_invalidate_folio to fix memory leak

## Summary
Severity: Medium
Advisory: CVE-2022-49550
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49550
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: provide block_invalidate_folio to fix memory leak

The ntfs3 filesystem lacks the 'invalidate_folio' method and it causes
memory leak. If you write to the filesystem and then unmount it, the
cached written data are not freed and they are permanently leaked.

## References
- https://git.kernel.org/stable/c/0753245a72ec99824677586499ee2e0919164b3f
- https://git.kernel.org/stable/c/724bbe49c5e427cb077357d72d240a649f2e4054
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49550.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
