# [C] smb: server: avoid double-free in smb_direct_free_sendmsg after smb_direct_flush_send_list()

## Summary
Severity: Critical
Advisory: CVE-2026-31608
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31608
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: server: avoid double-free in smb_direct_free_sendmsg after smb_direct_flush_send_list()

smb_direct_flush_send_list() already calls smb_direct_free_sendmsg(),
so we should not call it again after post_sendmsg()
moved it to the batch list.

## References
- https://git.kernel.org/stable/c/2ba03f46132b0d1a7bafb86e1ef61951a2254023
- https://git.kernel.org/stable/c/6968c91fab05b8fc4d6700e0cf34472bb422df25
- https://git.kernel.org/stable/c/830de6eeb9db4cb7e758201fb99328ef4ca4b032
- https://git.kernel.org/stable/c/84ff995ae826aa6bbcc6c7b9ea569ff67c021d72
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31608.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
