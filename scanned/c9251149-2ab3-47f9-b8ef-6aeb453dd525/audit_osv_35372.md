# [H] btrfs: fix reservation leak in some error paths when inserting inline extent

## Summary
Severity: High
Advisory: CVE-2025-71268
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-18
Source: https://osv.dev/vulnerability/CVE-2025-71268
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix reservation leak in some error paths when inserting inline extent

If we fail to allocate a path or join a transaction, we return from
__cow_file_range_inline() without freeing the reserved qgroup data,
resulting in a leak. Fix this by ensuring we call btrfs_qgroup_free_data()
in such cases.

## References
- https://git.kernel.org/stable/c/28768bd3abf9995a93f6e01bfce01c60622964dd
- https://git.kernel.org/stable/c/28b97fcbbf523779688e8de5fe55bf2dae3859f6
- https://git.kernel.org/stable/c/c1c050f92d8f6aac4e17f7f2230160794fceef0c
- https://git.kernel.org/stable/c/f3ee1732851aec6fe6b2cec2ef1b32d4e71d9913
- https://git.kernel.org/stable/c/f7156512c8166d385f574b9ec030479aa7b1e8c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71268.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
