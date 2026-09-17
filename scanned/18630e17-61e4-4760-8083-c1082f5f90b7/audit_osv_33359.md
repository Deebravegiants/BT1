# [H] ext4: guard against EA inode refcount underflow in xattr update

## Summary
Severity: High
Advisory: CVE-2025-40190
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40190
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: guard against EA inode refcount underflow in xattr update

syzkaller found a path where ext4_xattr_inode_update_ref() reads an EA
inode refcount that is already <= 0 and then applies ref_change (often
-1). That lets the refcount underflow and we proceed with a bogus value,
triggering errors like:

  EXT4-fs error: EA inode <n> ref underflow: ref_count=-1 ref_change=-1
  EXT4-fs warning: ea_inode dec ref err=-117

Make the invariant explicit: if the current refcount is non-positive,
treat this as on-disk corruption, emit ext4_error_inode(), and fail the
operation with -EFSCORRUPTED instead of updating the refcount. Delete the
WARN_ONCE() as negative refcounts are now impossible; keep error reporting
in ext4_error_inode().

This prevents the underflow and the follow-on orphan/cleanup churn.

## References
- https://git.kernel.org/stable/c/1cfb3e4ddbdc8e02e637b8852540bd4718bf4814
- https://git.kernel.org/stable/c/3d6269028246f4484bfed403c947a114bb583631
- https://git.kernel.org/stable/c/440b003f449a4ff2a00b08c8eab9ba5cd28f3943
- https://git.kernel.org/stable/c/505e69f76ac497e788f4ea0267826ec7266b40c8
- https://git.kernel.org/stable/c/57295e835408d8d425bef58da5253465db3d6888
- https://git.kernel.org/stable/c/6b879c4c6bbaab03c0ad2a983953bd1410bb165e
- https://git.kernel.org/stable/c/79ea7f3e11effe1bd9e753172981d9029133a278
- https://git.kernel.org/stable/c/ea39e712c2f5ae148ee5515798ae03523673e002
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40190.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40190
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
