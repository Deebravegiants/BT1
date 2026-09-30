# [H] nilfs2: protect access to buffers with no active references

## Summary
Severity: High
Advisory: CVE-2025-21811
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21811
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: protect access to buffers with no active references

nilfs_lookup_dirty_data_buffers(), which iterates through the buffers
attached to dirty data folios/pages, accesses the attached buffers without
locking the folios/pages.

For data cache, nilfs_clear_folio_dirty() may be called asynchronously
when the file system degenerates to read only, so
nilfs_lookup_dirty_data_buffers() still has the potential to cause use
after free issues when buffers lose the protection of their dirty state
midway due to this asynchronous clearing and are unintentionally freed by
try_to_free_buffers().

Eliminate this race issue by adjusting the lock section in this function.

## References
- https://git.kernel.org/stable/c/367a9bffabe08c04f6d725032cce3d891b2b9e1a
- https://git.kernel.org/stable/c/4b08d23d7d1917bef4fbee8ad81372f49b006656
- https://git.kernel.org/stable/c/58c27fa7a610b6e8d44e6220e7dbddfbaccaf439
- https://git.kernel.org/stable/c/72cf688d0ce7e642b12ddc9b2a42524737ec1b4a
- https://git.kernel.org/stable/c/8e1b9201c9a24638cf09c6e1c9f224157328010b
- https://git.kernel.org/stable/c/c437dfac9f7a5a46ac2a5e6d6acd3059e9f68188
- https://git.kernel.org/stable/c/d8ff250e085a4c4cdda4ad1cdd234ed110393143
- https://git.kernel.org/stable/c/e1fc4a90a90ea8514246c45435662531975937d9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21811.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21811
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
