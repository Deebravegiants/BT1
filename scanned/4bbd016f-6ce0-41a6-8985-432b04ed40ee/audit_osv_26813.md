# [C] smb: client: fix missed ses refcounting

## Summary
Severity: Critical
Advisory: CVE-2023-54076
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54076
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix missed ses refcounting

Use new cifs_smb_ses_inc_refcount() helper to get an active reference
of @ses and @ses->dfs_root_ses (if set).  This will prevent
@ses->dfs_root_ses of being put in the next call to cifs_put_smb_ses()
and thus potentially causing an use-after-free bug.

## References
- https://git.kernel.org/stable/c/bf99f6be2d20146942bce6f9e90a0ceef12cbc1e
- https://git.kernel.org/stable/c/eb382196e6f6e05cfafdab797840e5a96c6e7bf0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54076.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54076
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
