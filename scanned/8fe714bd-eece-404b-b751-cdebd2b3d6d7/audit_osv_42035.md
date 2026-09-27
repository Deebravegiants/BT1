# [C] smb: client: fix query_info() replay double-free

## Summary
Severity: Critical
Advisory: CVE-2026-64386
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64386
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.96, >=6.8.0 <6.18.39, >=6.13.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix query_info() replay double-free

A response-bearing attempt can return a replayable error and free its
response buffer. If SMB2_query_info_init() fails before the next send,
cleanup retains the previous buffer type and frees that response again.

Reset response bookkeeping before each attempt to prevent the stale free.

## References
- https://git.kernel.org/stable/c/100fb7c455fa86d248b8bd7bb9de757c192870b4
- https://git.kernel.org/stable/c/2a88561d66eb855813cf004a0abe648bbb17de5e
- https://git.kernel.org/stable/c/3c81dda84799f76b42aec598564316e2964440db
- https://git.kernel.org/stable/c/89234773e8348918111aa15f6922b58cf3843364
- https://git.kernel.org/stable/c/f1add4acb656f5a82806a1ab0e63fed3d8b1bfca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64386.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64386
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
