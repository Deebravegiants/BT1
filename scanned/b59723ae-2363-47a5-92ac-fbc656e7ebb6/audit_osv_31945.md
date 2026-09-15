# [H] bcachefs: bch2_ioctl_subvolume_destroy() fixes

## Summary
Severity: High
Advisory: CVE-2025-22019
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22019
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.22, >=6.13.0 <6.13.10, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bcachefs: bch2_ioctl_subvolume_destroy() fixes

bch2_evict_subvolume_inodes() was getting stuck - due to incorrectly
pruning the dcache.

Also, fix missing permissions checks.

## References
- https://git.kernel.org/stable/c/558317a5c61045d460a37372181e7b43c0c002bb
- https://git.kernel.org/stable/c/707549600c4a012ed71c0204a7992a679880bf33
- https://git.kernel.org/stable/c/82383abd39abd635511b8956284a5cc8134c4dc1
- https://git.kernel.org/stable/c/9e6e83e1e2d01b99e70cd7812d7f758a8def9fc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22019.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
