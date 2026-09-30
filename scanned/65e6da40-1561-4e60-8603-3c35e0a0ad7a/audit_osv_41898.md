# [H] netfs: Fix netfs_read_folio() to wait on writeback

## Summary
Severity: High
Advisory: CVE-2026-64058
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64058
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfs: Fix netfs_read_folio() to wait on writeback

Fix netfs_read_folio() to wait for an ongoing writeback to complete so that
it can trust the dirty flag and whatever is attached to folio->private
(folio->private may get cleaned up by the collector before it clears the
writeback flag).

## References
- https://git.kernel.org/stable/c/b8271cccdd5e43cc8d738afb8b51f6ad05b1cb4b
- https://git.kernel.org/stable/c/ded0c6f1606061148c202825f7e53d711f9f84cf
- https://git.kernel.org/stable/c/f17b9121bb99f88188ec9be2db5da1d561f4c01b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64058.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64058
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
