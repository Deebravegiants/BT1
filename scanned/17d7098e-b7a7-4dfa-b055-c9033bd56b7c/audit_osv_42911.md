# [C] xfrm: nat_keepalive: avoid double free on send error

## Summary
Severity: Critical
Advisory: CVE-2026-72137
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72137
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: nat_keepalive: avoid double free on send error

nat_keepalive_send() frees the keepalive skb whenever the IPv4 or IPv6
send helper reports an error.

That cleanup is only correct before the skb is handed to the output
path. Once ip_build_and_send_pkt() or ip6_xmit() takes ownership, the
networking stack may already have consumed the skb before returning an
error, so freeing it again is unsafe.

Handle the pre-handoff failure cases inside nat_keepalive_send_ipv4()
and nat_keepalive_send_ipv6(), where the caller still owns the skb, and
keep nat_keepalive_send() responsible only for family dispatch and the
unsupported-family cleanup path.

## References
- https://git.kernel.org/stable/c/226f4a490d1a938fc838d8f8c46a4eca864c0d78
- https://git.kernel.org/stable/c/5b0c4c916f202b8fd13d12afb6af62b385622f81
- https://git.kernel.org/stable/c/a8a7e6a9ff8a4c1f067694ddbd44be67fdf36693
- https://git.kernel.org/stable/c/d0a4dc7efa825bce60a8da8f7d43c864a159abde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72137.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
