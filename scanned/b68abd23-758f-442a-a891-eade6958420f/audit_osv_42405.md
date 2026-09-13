# [C] ksmbd: fix path resolution in ksmbd_vfs_kern_path_create

## Summary
Severity: Critical
Advisory: CVE-2026-68083
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68083
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix path resolution in ksmbd_vfs_kern_path_create

The SMB2 open lookup is rooted at the share with LOOKUP_BENEATH, but the
create/mkdir/hardlink sink is not: ksmbd_vfs_kern_path_create() builds an
absolute path with convert_to_unix_name() and resolves it from AT_FDCWD
via start_creating_path(), so a ".." component is walked from the real
filesystem root and escapes the export.

An authenticated client races a missing path component so the rooted open
lookup returns -ENOENT (taking the create branch) while the same component
is present (a directory) when the create walk runs; the create then
resolves ".." out of the share.

Root the create walk at the share like the lookup and rename paths already
are: resolve the parent with vfs_path_parent_lookup(..., LOOKUP_BENEATH,
&share_conf->vfs_path) and create the final component with
start_creating_noperm(). convert_to_unix_name() then has no callers and is
removed.

## References
- https://git.kernel.org/stable/c/1c8951963d8ed357f70f59e0ad4ddce2199d2016
- https://git.kernel.org/stable/c/489d1ded01425c0fb33418172c0e4e588467526b
- https://git.kernel.org/stable/c/98185b3025beeae92d1fe700d5db26b9ac4bf025
- https://git.kernel.org/stable/c/c7c884a1305aa4540eb7942a50bd356b34120e1f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68083.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68083
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
