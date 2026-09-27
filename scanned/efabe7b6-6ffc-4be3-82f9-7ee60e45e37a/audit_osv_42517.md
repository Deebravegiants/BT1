# [C] smb: client: validate DFS referral PathConsumed

## Summary
Severity: Critical
Advisory: CVE-2026-68343
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68343
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: validate DFS referral PathConsumed

parse_dfs_referrals() validates that the response contains the fixed
referral entry array and, on for-next, the per-referral string offsets.
However, the response also contains a PathConsumed value that is later
used for DFS path parsing.

If a malformed response provides a PathConsumed value larger than the
search name, later DFS parsing can advance beyond the end of the path.

Validate PathConsumed against the search name length before storing it in
the parsed referral.

## References
- https://git.kernel.org/stable/c/285bd4a5f3f156aa5869843b47a1b1380b774241
- https://git.kernel.org/stable/c/2fdd6d196c656b376cc251e1e9ff110b3ed522e1
- https://git.kernel.org/stable/c/5b439f39f33ec15d319ced3b025e122346fba987
- https://git.kernel.org/stable/c/9f88a99ed511651b2dc2177d6854b2d1b8322e75
- https://git.kernel.org/stable/c/bfebe5110fd135d86d65a0a346e14c106b02028b
- https://git.kernel.org/stable/c/f6f5ee2aa33b350c671721b965251c42cebb962e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68343.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
