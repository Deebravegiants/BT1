# [M] tarfile extraction filter bypass allows creation of directories outside the destination

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-19672
Aliases: BIT-python-2026-19672, BIT-python-min-2026-19672, CVE-2026-19672, PSF-2026-38
Ecosystem: Bitnami
Published: 2026-08-25
Source: https://osv.dev/vulnerability/BIT-libpython-2026-19672
Type: osv

## Affected
- Bitnami: `libpython` — affected unspecified

## Details
The tarfile module's tar and data
 extraction filters created directories outside the destination for 
members whose name leaves the destination and returns to it, such as ../evil/../dest/sub/file. The containment check used the resolved path, but intermediate directories were created from the name as given.

Only
 empty directories are created outside the destination. Member contents 
are still extracted inside it. To return to the destination the member's
 name must contain the destination directory's own final component, so 
extraction into a secure randomised directory is not affected.

This affects POSIX platforms only. On Windows, .. components are collapsed before the path reaches the filesystem, so the directories outside the destination are never created.

## References
- https://github.com/python/cpython/pull/156000
- https://mail.python.org/archives/list/security-announce@python.org/thread/J2WT2ALRWEXQJOB3C7Q2HYWUXP3CINWO/
- https://nvd.nist.gov/vuln/detail/CVE-2026-19672
- http://www.openwall.com/lists/oss-security/2026/08/25/10
