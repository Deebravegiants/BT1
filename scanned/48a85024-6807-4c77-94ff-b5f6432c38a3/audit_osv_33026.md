# [H] f2fs: fix KMSAN uninit-value in extent_info usage

## Summary
Severity: High
Advisory: CVE-2025-38579
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38579
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix KMSAN uninit-value in extent_info usage

KMSAN reported a use of uninitialized value in `__is_extent_mergeable()`
 and `__is_back_mergeable()` via the read extent tree path.

The root cause is that `get_read_extent_info()` only initializes three
fields (`fofs`, `blk`, `len`) of `struct extent_info`, leaving the
remaining fields uninitialized. This leads to undefined behavior
when those fields are accessed later, especially during
extent merging.

Fix it by zero-initializing the `extent_info` struct before population.

## References
- https://git.kernel.org/stable/c/01b6f5955e0008af6bc3a181310d2744bb349800
- https://git.kernel.org/stable/c/08e8ab00a6d20d5544c932ee85a297d833895141
- https://git.kernel.org/stable/c/154467f4ad033473e5c903a03e7b9bca7df9a0fa
- https://git.kernel.org/stable/c/44a79437309e0ee2276ac17aaedc71253af253a8
- https://git.kernel.org/stable/c/cc1615d5aba4f396cf412579928539a2b124c8a0
- https://git.kernel.org/stable/c/dabfa3952c8e6bfe6414dbf32e8b6c5f349dc898
- https://git.kernel.org/stable/c/e68b751ec2b15d866967812c57cfdfc1eba6a269
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38579.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38579
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
