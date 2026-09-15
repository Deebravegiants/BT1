# [H] smb: client: fix incomplete backport in cfids_invalidation_worker()

## Summary
Severity: High
Advisory: CVE-2025-68226
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68226
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.8 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix incomplete backport in cfids_invalidation_worker()

The previous commit bdb596ceb4b7 ("smb: client: fix potential UAF in
smb2_close_cached_fid()") was an incomplete backport and missed one
kref_put() call in cfids_invalidation_worker() that should have been
converted to close_cached_dir().

## References
- https://git.kernel.org/stable/c/abd29b6e17a918fdd68352ce4813e167acc8727e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68226.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
