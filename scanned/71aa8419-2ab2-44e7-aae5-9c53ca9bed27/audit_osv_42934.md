# [C] ntfs: sanitize MFT references returned from ntfs_lookup_inode_by_name()

## Summary
Severity: Critical
Advisory: CVE-2026-72188
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72188
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: sanitize MFT references returned from ntfs_lookup_inode_by_name()

ntfs_lookup_inode_by_name() returns MFT references read from directory
index entries on disk. These values are untrusted, but the function can
currently return an error-marked MFT reference to its callers without
validating it.

Callers later decode lookup failures with MREF_ERR(). A crafted NTFS image
can set the MREF error bit while leaving the low bits as an arbitrary
value, causing callers to consume a bogus pseudo-errno instead of treating
the lookup result as corrupted on-disk metadata.

Fix this at the source by normalizing every error-marked MFT reference
returned from ntfs_lookup_inode_by_name() to ERR_MREF(-EIO). Apply this to
all four directory lookup return paths so every caller gets a validated
result without needing additional checks or an API change.

This keeps the sanitization in the common lookup helper, which is cleaner
than duplicating validation in each caller.

## References
- https://git.kernel.org/stable/c/83f396d881c4fd312c7fd5fff2c157fc21104464
- https://git.kernel.org/stable/c/d97a36bae86a9a4021562ded2987f904e6bcb1d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72188
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
