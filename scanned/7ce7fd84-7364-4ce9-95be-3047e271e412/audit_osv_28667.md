# [C] smb: client: guarantee refcounted children from parent session

## Summary
Severity: Critical
Advisory: CVE-2024-35869
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35869
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.29, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: guarantee refcounted children from parent session

Avoid potential use-after-free bugs when walking DFS referrals,
mounting and performing DFS failover by ensuring that all children
from parent @tcon->ses are also refcounted.  They're all needed across
the entire DFS mount.  Get rid of @tcon->dfs_ses_list while we're at
it, too.

## References
- https://git.kernel.org/stable/c/062a7f0ff46eb57aff526897bd2bebfdb1d3046a
- https://git.kernel.org/stable/c/645f332c6b63499cc76197f9b6bffcc659ba64cc
- https://git.kernel.org/stable/c/e1db9ae87b7148c021daee1fcc4bc71b2ac58a79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35869.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35869
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
