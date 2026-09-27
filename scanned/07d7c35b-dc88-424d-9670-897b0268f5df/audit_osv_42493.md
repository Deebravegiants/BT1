# [H] drop_monitor: fix size calculations for 64-bit attributes

## Summary
Severity: High
Advisory: CVE-2026-68287
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68287
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drop_monitor: fix size calculations for 64-bit attributes

net_dm_packet_report_fill() and net_dm_hw_packet_report_fill() use
nla_put_u64_64bit() to append 64-bit attributes (NET_DM_ATTR_PC and
NET_DM_ATTR_TIMESTAMP).

On 32-bit architectures without CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS,
nla_put_u64_64bit() may append a 4-byte NET_DM_ATTR_PAD attribute for
64-bit alignment.

However, net_dm_packet_report_size() and net_dm_hw_packet_report_size()
used nla_total_size(sizeof(u64)) instead of nla_total_size_64bit(sizeof(u64)),
budgeting 12 bytes instead of up to 16 bytes.

This under-estimation of SKB size can lead to an skb_over_panic() when
__nla_reserve() or skb_put() is subsequently called.

Fix this by using nla_total_size_64bit(sizeof(u64)) in both size calculations.

## References
- https://git.kernel.org/stable/c/4a9e30764e80693bcf875c776170edce20f94fe0
- https://git.kernel.org/stable/c/7089f7ab99c89f443c92d8fcc585e63f2727f0b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
