# [C] smb: client: fix query directory replay double-free

## Summary
Severity: Critical
Advisory: CVE-2026-64387
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64387
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix query directory replay double-free

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_query_directory_init() fails before the next send,
cleanup retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/00b0fa425941438b664950a8ee65dfba2def4336
- https://git.kernel.org/stable/c/1665f25b1dea30bf2d02e16245d203a944c9d994
- https://git.kernel.org/stable/c/3317a5d015fca976475aa71df224056777316fde
- https://git.kernel.org/stable/c/3409aedf3c81a810243da94164f6621c9d205c98
- https://git.kernel.org/stable/c/9647492b5e41954be59d5157eddbcd4cdc1656f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64387.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64387
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
