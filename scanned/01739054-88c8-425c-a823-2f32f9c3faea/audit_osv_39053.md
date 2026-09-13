# [H] net-shapers: don't free reply skb after genlmsg_reply()

## Summary
Severity: High
Advisory: CVE-2026-43481
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-43481
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net-shapers: don't free reply skb after genlmsg_reply()

genlmsg_reply() hands the reply skb to netlink, and
netlink_unicast() consumes it on all return paths, whether the
skb is queued successfully or freed on an error path.

net_shaper_nl_get_doit() and net_shaper_nl_cap_get_doit()
currently jump to free_msg after genlmsg_reply() fails and call
nlmsg_free(msg), which can hit the same skb twice.

Return the genlmsg_reply() error directly and keep free_msg
only for pre-reply failures.

## References
- https://git.kernel.org/stable/c/57885276cc16a2e2b76282c808a4e84cbecb3aae
- https://git.kernel.org/stable/c/83f7b54242d0abbfce35a55c01322f50962ed3ee
- https://git.kernel.org/stable/c/8738dcc844fff7d0157ee775230e95df3b1884d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43481.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43481
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
