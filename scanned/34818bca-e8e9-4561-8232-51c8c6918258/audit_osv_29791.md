# [H] btrfs: don't BUG_ON() when 0 reference count at btrfs_lookup_extent_info()

## Summary
Severity: High
Advisory: CVE-2024-46751
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46751
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.31 <5.10.238, >=5.11.0 <5.15.184, >=5.16.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: don't BUG_ON() when 0 reference count at btrfs_lookup_extent_info()

Instead of doing a BUG_ON() handle the error by returning -EUCLEAN,
aborting the transaction and logging an error message.

## References
- https://git.kernel.org/stable/c/18eb53a2734ff61b9a72c4fef5db7b38cb48ae16
- https://git.kernel.org/stable/c/28cb13f29faf6290597b24b728dc3100c019356f
- https://git.kernel.org/stable/c/3cfec712a439c5c5f5c718c5c669ee41a898f776
- https://git.kernel.org/stable/c/9c309d2434abbe880712af7e60da9ead8b6703fe
- https://git.kernel.org/stable/c/d64807ded1b6054f066e03d8add6d920f3db9e5d
- https://git.kernel.org/stable/c/ef9a8b73c8b60b27d9db4787e624a3438ffe8428
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46751.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
