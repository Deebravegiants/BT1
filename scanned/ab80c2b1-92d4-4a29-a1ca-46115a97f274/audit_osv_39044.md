# [H] netfilter: nf_tables: Fix for duplicate device in netdev hooks

## Summary
Severity: High
Advisory: CVE-2026-43454
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43454
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: Fix for duplicate device in netdev hooks

When handling NETDEV_REGISTER notification, duplicate device
registration must be avoided since the device may have been added by
nft_netdev_hook_alloc() already when creating the hook.

## References
- https://git.kernel.org/stable/c/2041cdb078041611510fc189410bc70b29f688fb
- https://git.kernel.org/stable/c/6d2a95c6890577cc3eab2b20018e16850d7fb094
- https://git.kernel.org/stable/c/b7cdc5a97d02c943f4bdde4d5767ad0c13cad92b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43454.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
