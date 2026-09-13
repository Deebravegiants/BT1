# [C] udp: fix potential use-after-free in tunnel segmentation

## Summary
Severity: Critical
Advisory: CVE-2026-74705
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74705
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

udp: fix potential use-after-free in tunnel segmentation

__skb_udp_tunnel_segment() gets the UDP header before ensuring the
tunnel header is in the skb head. If the pull reallocates skb->head,
the saved UDP header pointer is no longer valid.

Get the UDP header after the pull to avoid a potential use-after-free.

## References
- https://git.kernel.org/stable/c/19d89b13a43640b2da2f277ee462d919d988cb6f
- https://git.kernel.org/stable/c/1ae134c012e10384cdac420b5cc6e0615cde0b55
- https://git.kernel.org/stable/c/5161e67c561c4f28a5d9335a6e859b02511de92b
- https://git.kernel.org/stable/c/588d4a6795d99d080f74ef0b5f391ea8c453ae5d
- https://git.kernel.org/stable/c/64d322c288577793eedd352b96ef75234ed380fe
- https://git.kernel.org/stable/c/6a733a38b983d8c2e222f13968209010cf44de87
- https://git.kernel.org/stable/c/b3df61bb745eb5201eac22679a2839d4ccbf3442
- https://git.kernel.org/stable/c/d0f86fb36eb260abd10007b62c9dcc1028e03e61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74705.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74705
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
