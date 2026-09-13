# [H] ipv6: Fix out-of-bounds access in ipv6_find_tlv()

## Summary
Severity: High
Advisory: CVE-2023-53705
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2023-53705
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.114, >=5.16.0 <6.1.31, >=6.2.0 <6.3.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: Fix out-of-bounds access in ipv6_find_tlv()

optlen is fetched without checking whether there is more than one byte to parse.
It can lead to out-of-bounds access.

Found by InfoTeCS on behalf of Linux Verification Center
(linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/011f47c8b8389154f996f5f69da8efc3a3beefef
- https://git.kernel.org/stable/c/04bf69e3de435d793a203aacc4b774f8f9f2baeb
- https://git.kernel.org/stable/c/59e656d0d4a84ea0ee9a39c6f69160a3effccc94
- https://git.kernel.org/stable/c/878ecb0897f4737a4c9401f3523fd49589025671
- https://git.kernel.org/stable/c/91dd8aab9c9f193210681b86b6b92840ffe74f0c
- https://git.kernel.org/stable/c/9b92e2d0eb696d7586ba832c8854653b59887da0
- https://git.kernel.org/stable/c/ae68c0f7edbc9a294094ce03a0aaf45aa489ce40
- https://git.kernel.org/stable/c/e5f82688ae10f5f386952e65e941bb8868ee54dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53705.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53705
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
