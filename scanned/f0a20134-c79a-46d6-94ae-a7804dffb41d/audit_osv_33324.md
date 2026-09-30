# [C] cifs: parse_dfs_referrals: prevent oob on malformed input

## Summary
Severity: Critical
Advisory: CVE-2025-40099
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-40099
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.158, >=6.2.0 <6.6.114, >=6.7.0 <6.12.55, >=6.13.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: parse_dfs_referrals: prevent oob on malformed input

Malicious SMB server can send invalid reply to FSCTL_DFS_GET_REFERRALS

- reply smaller than sizeof(struct get_dfs_referral_rsp)
- reply with number of referrals smaller than NumberOfReferrals in the
header

Processing of such replies will cause oob.

Return -EINVAL error on such replies to prevent oob-s.

## References
- https://git.kernel.org/stable/c/15c73964da9df994302f579ed14ee5fdbce7a332
- https://git.kernel.org/stable/c/6447b0e355562a1ff748c4a2ffb89aae7e84d2c9
- https://git.kernel.org/stable/c/8bc4a8d39bac23d8b044fd3e2dbfd965f1d9b058
- https://git.kernel.org/stable/c/bb0f2e66e1ac043a5b238f5bcab4f26f3c317039
- https://git.kernel.org/stable/c/cfacc7441f760e4a73cc71b6ff1635261d534657
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40099.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40099
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
