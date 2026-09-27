# [H] net: do not send ICMP/NDISC Redirects when peer allocation fails

## Summary
Severity: High
Advisory: CVE-2026-74550
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74550
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: do not send ICMP/NDISC Redirects when peer allocation fails

When inet_getpeer_v4() or inet_getpeer_v6() fails to allocate a peer entry
under memory pressure or tree size caps, redirect handlers previously fell
back to sending un-rate-limited ICMP/NDISC Redirect messages.

In IPv4, ip_rt_send_redirect() called icmp_send() directly when peer == NULL.
In IPv6, ip6_forward() and ndisc_send_redirect() passed a NULL peer into
inet_peer_xrlim_allow(), which returned true when peer == NULL.

Because ICMP/NDISC Redirects are not part of the default global rate limit
mask (sysctl_icmp_ratemask), sending redirects when peer == NULL creates
an un-rate-limited ICMP packet storm.

Fix this by failing closed in ip_rt_send_redirect(), ip6_forward(), and
ndisc_send_redirect() when peer is NULL.

## References
- https://git.kernel.org/stable/c/21666f7af49a90ef44d474916b8ef4402dfd74f5
- https://git.kernel.org/stable/c/5ec5f00fc606a6df8434948c4552b3cb1176595d
- https://git.kernel.org/stable/c/828f6670d110ff2bf44c743037b38badc315704c
- https://git.kernel.org/stable/c/c0adf8b4247bcc5a145a25c1929006eb392580bb
- https://git.kernel.org/stable/c/dbc3791e3b2472e1ccc08947e0f83b443470ff4f
- https://git.kernel.org/stable/c/f5ecaa7ea7686fa7ecdb6affc9d3a9a42e4524b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74550.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74550
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
