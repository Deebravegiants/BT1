# [C] vxlan: re-fetch eth header after route_shortcircuit()

## Summary
Severity: Critical
Advisory: CVE-2026-80681
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80681
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: re-fetch eth header after route_shortcircuit()

Before route_shortcircuit(), the eth header pointer is cached from eth_hdr(skb).

Inside route_shortcircuit(), pskb_may_pull() can be called, which may
reallocate skb->head.

In this case, returning to vxlan_xmit() leaves the cached eth pointer pointing to
freed memory, leading to a use-after-free when dereferencing eth->h_dest.

Fix this by updating eth = eth_hdr(skb) after calling route_shortcircuit().

## References
- https://git.kernel.org/stable/c/1235e017aa11cf01e91b613c4c5ed6aa28934fff
- https://git.kernel.org/stable/c/1395a676ec15a0a02a2a6d86602324f2d5fd41d5
- https://git.kernel.org/stable/c/1511631b7cfc4152b10a0a9d04c7a0bf2ddf4585
- https://git.kernel.org/stable/c/1b7f7b653e3557690047c62f03b80a24ea5a58a5
- https://git.kernel.org/stable/c/2355c8c26d2aa1b4385b369e67202e47d460d555
- https://git.kernel.org/stable/c/6375093eb45cd7d89f1945f939eeae3b29d79f56
- https://git.kernel.org/stable/c/bf045341dfb3e767f0ff94cf240ce3c371973bd4
- https://git.kernel.org/stable/c/c9dceac9e1c7c772c43c732fc0d325e72835801a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80681.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80681
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
