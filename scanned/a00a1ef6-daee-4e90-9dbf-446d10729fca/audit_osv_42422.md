# [H] pppoe: reload header pointer after dev_hard_header()

## Summary
Severity: High
Advisory: CVE-2026-68121
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68121
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

pppoe: reload header pointer after dev_hard_header()

pppoe_sendmsg() saves a pointer to the PPPoE header before calling
dev_hard_header(). Device header callbacks are allowed to reallocate the
skb head, invalidating pointers into it.

This can happen when a send is blocked in copy_from_user() while the first
non-Ethernet port is added to an empty team device. The team's delegated
GRE header callback then expands the skb head. PPPoE subsequently writes
six bytes through the stale pointer into the freed head.

Reload the PPPoE header through the skb's network-header offset after
device header creation. pskb_expand_head() updates that offset when it
relocates the head.

## References
- https://git.kernel.org/stable/c/6866abf59976d273164a6624234d96a967280223
- https://git.kernel.org/stable/c/6eed5ae7887a93160803d2b81ff88e75eefd4a4c
- https://git.kernel.org/stable/c/7a56e7c9b08e08fd55a1bcada24cf4fe3782b722
- https://git.kernel.org/stable/c/7e9fbd7f96bcde63a7c798fe16b38cedee7a1501
- https://git.kernel.org/stable/c/ba3409369c5413cdf0dcbf3a928f76b48e8c3e6a
- https://git.kernel.org/stable/c/bed4caecd723693f750e13adbb2c42ca1249a3fd
- https://git.kernel.org/stable/c/e6493a4d1ee17595766165fa446d45b7e0c318d0
- https://git.kernel.org/stable/c/e9c238f6fe42fb1b4dba3a578277de32cb487937
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68121.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68121
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
