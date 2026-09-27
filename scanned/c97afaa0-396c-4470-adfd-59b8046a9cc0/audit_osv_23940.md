# [M] 9p: fix fid refcount leak in v9fs_vfs_atomic_open_dotl

## Summary
Severity: Medium
Advisory: CVE-2022-49705
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49705
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: fix fid refcount leak in v9fs_vfs_atomic_open_dotl

We need to release directory fid if we fail halfway through open

This fixes fid leaking with xfstests generic 531

## References
- https://git.kernel.org/stable/c/22832ac3eb5be3f7168816a76b64c1284e12eb3c
- https://git.kernel.org/stable/c/8bc5412ba1a45edfd1e451874c483c26a097af2b
- https://git.kernel.org/stable/c/beca774fc51a9ba8abbc869cf0c3d965ff17cd24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49705.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49705
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
