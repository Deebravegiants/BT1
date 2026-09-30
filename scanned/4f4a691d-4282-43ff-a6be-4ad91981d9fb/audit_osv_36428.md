# [H] ip_tunnel: adapt iptunnel_xmit_stats() to NETDEV_PCPU_STAT_DSTATS

## Summary
Severity: High
Advisory: CVE-2026-23459
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23459
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.50, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip_tunnel: adapt iptunnel_xmit_stats() to NETDEV_PCPU_STAT_DSTATS

Blamed commits forgot that vxlan/geneve use udp_tunnel[6]_xmit_skb() which
call iptunnel_xmit_stats().

iptunnel_xmit_stats() was assuming tunnels were only using
NETDEV_PCPU_STAT_TSTATS.

@syncp offset in pcpu_sw_netstats and pcpu_dstats is different.

32bit kernels would either have corruptions or freezes if the syncp
sequence was overwritten.

This patch also moves pcpu_stat_type closer to dev->{t,d}stats to avoid
a potential cache line miss since iptunnel_xmit_stats() needs to read it.

## References
- https://git.kernel.org/stable/c/0d087d00161f562d5047cc4009bb0c6a19daf9f1
- https://git.kernel.org/stable/c/5d562153b4719234227f99c2fb529f98a6a44d15
- https://git.kernel.org/stable/c/8431c602f551549f082bbfa67f3003f2d8e3e132
- https://git.kernel.org/stable/c/e40e2d11ced8119d3e4469ebe91264bc1cf71530
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
