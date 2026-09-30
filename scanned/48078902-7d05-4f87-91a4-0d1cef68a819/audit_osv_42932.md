# [C] ntfs: fix WARN_ON for resident attribute in ntfs_map_runlist_nolock()

## Summary
Severity: Critical
Advisory: CVE-2026-72185
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72185
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: fix WARN_ON for resident attribute in ntfs_map_runlist_nolock()

When ntfs_map_runlist_nolock() needs to look up the attribute extent
containing a target VCN (ctx_needs_reset == true), it calls
ntfs_attr_lookup() and then expects the result to be a non-resident
attribute, since only non-resident attributes have a mapping pairs
array to decompress.

A crafted NTFS image can place a resident attribute where a non-resident
one is expected, causing ntfs_attr_lookup() to succeed but return a
resident attribute record.  Previously this was caught only by a
WARN_ON(), which does not stop execution.  The code then falls through to
read a->data.non_resident.highest_vcn from what is actually a resident
attribute, accessing the wrong union member and corrupting the VCN range
check.

The caller path triggering this warning during mount is:

  ntfs_map_runlist_nolock
  ntfs_empty_logfile
  load_system_files
  ntfs_fill_super

In this path ctx is NULL, so ntfs_map_runlist_nolock() allocates a
temporary search context internally and sets ctx_needs_reset = true.
The existing resident-attribute guard in the ctx != NULL branch already
returns -EIO silently for the same condition; make the ctx_needs_reset
path consistent by replacing the WARN_ON() with the same -EIO error
return.

This causes the crafted image to be rejected with a mount error instead
of triggering a kernel warning.

## References
- https://git.kernel.org/stable/c/b397b1238a217264bb02f963a1a1eadf71906375
- https://git.kernel.org/stable/c/b8d6c528e9d57d263fee1a648409f84a68b2561d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72185.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72185
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
