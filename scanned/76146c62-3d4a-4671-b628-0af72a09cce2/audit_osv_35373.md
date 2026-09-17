# [H] btrfs: do not free data reservation in fallback from inline due to -ENOSPC

## Summary
Severity: High
Advisory: CVE-2025-71269
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2025-71269
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: do not free data reservation in fallback from inline due to -ENOSPC

If we fail to create an inline extent due to -ENOSPC, we will attempt to
go through the normal COW path, reserve an extent, create an ordered
extent, etc. However we were always freeing the reserved qgroup data,
which is wrong since we will use data. Fix this by freeing the reserved
qgroup data in __cow_file_range_inline() only if we are not doing the
fallback (ret is <= 0).

## References
- https://git.kernel.org/stable/c/0a1fbbd780f04d1b6cf48dd327c866ba937de1c4
- https://git.kernel.org/stable/c/3a9fd45afadec1fbfec72057b9473d509fa8b68c
- https://git.kernel.org/stable/c/3edd1f6c7c520536b62b2904807033597554dbac
- https://git.kernel.org/stable/c/6de3a371a8b9fd095198b1aa68c22cc10a4c6961
- https://git.kernel.org/stable/c/f8da41de0bff9eb1d774a7253da0c9f637c4470a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71269.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
