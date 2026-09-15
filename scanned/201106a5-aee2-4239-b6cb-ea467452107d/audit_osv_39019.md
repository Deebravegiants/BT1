# [H] net: ncsi: fix skb leak in error paths

## Summary
Severity: High
Advisory: CVE-2026-43373
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43373
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ncsi: fix skb leak in error paths

Early return paths in NCSI RX and AEN handlers fail to release
the received skb, resulting in a memory leak.

Specifically, ncsi_aen_handler() returns on invalid AEN packets
without consuming the skb. Similarly, ncsi_rcv_rsp() exits early
when failing to resolve the NCSI device, response handler, or
request, leaving the skb unfreed.

## References
- https://git.kernel.org/stable/c/553366c271479c0d571dd1bb5d1bcde4747fb82e
- https://git.kernel.org/stable/c/59962588197863d0d746879f193905c0c6b3df49
- https://git.kernel.org/stable/c/5c3398a54266541610c8d0a7082e654e9ff3e259
- https://git.kernel.org/stable/c/81d6aee32f8f7bbc175c05dbf61f4430bfb88c4a
- https://git.kernel.org/stable/c/87138dde2d6937b12b967f28fe598a7d59000ae4
- https://git.kernel.org/stable/c/9891d7f4f1ede473c54b49776ae07755083eef06
- https://git.kernel.org/stable/c/b70c4e5e711931cdd56e6e905737b72f1e649189
- https://git.kernel.org/stable/c/fef5aa6e3bcf3c8053307642663a63b7362d7552
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43373
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
