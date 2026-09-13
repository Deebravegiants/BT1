# [H] f2fs: fix listxattr handling of corrupted xattr entries

## Summary
Severity: High
Advisory: CVE-2026-80591
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80591
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix listxattr handling of corrupted xattr entries

Validate the xattr entry before reading its fields in f2fs_listxattr().
Return -EFSCORRUPTED when the entry is outside the valid xattr storage
area instead of returning a successful partial result.

## References
- https://git.kernel.org/stable/c/2770041f34b52334ea63351ffb1cc2007a9de46e
- https://git.kernel.org/stable/c/3c0dbfecd859fd02fe9008f33a83146102ccd9ba
- https://git.kernel.org/stable/c/5ef5bc304f23c3fe255d4936472378dcb74d0e94
- https://git.kernel.org/stable/c/7dd01f7d0291583e3e5420c95c7d584e114899bd
- https://git.kernel.org/stable/c/7dfac47e4189692f35230f3064acf2540e6d75fe
- https://git.kernel.org/stable/c/c8a10f174316e80d577e6549099b71a7a2111f3f
- https://git.kernel.org/stable/c/dfa4891c27bccbd83d511a065721e85621f275a1
- https://git.kernel.org/stable/c/ec9f79c8d5b28a928e65b67cd138c841571cf502
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80591.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80591
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
