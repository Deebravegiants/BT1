# [H] ipv6: mcast: add RCU protection to mld_newpack()

## Summary
Severity: High
Advisory: CVE-2025-21758
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21758
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: mcast: add RCU protection to mld_newpack()

mld_newpack() can be called without RTNL or RCU being held.

Note that we no longer can use sock_alloc_send_skb() because
ipv6.igmp_sk uses GFP_KERNEL allocations which can sleep.

Instead use alloc_skb() and charge the net->ipv6.igmp_sk
socket under RCU protection.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1b91c597b0214b1b462eb627ec02658c944623f2
- https://git.kernel.org/stable/c/25195f9d5ffcc8079ad743a50c0409dbdc48d98a
- https://git.kernel.org/stable/c/29fa42197f26a97cde29fa8c40beddf44ea5c8f3
- https://git.kernel.org/stable/c/a527750d877fd334de87eef81f1cb5f0f0ca3373
- https://git.kernel.org/stable/c/d60d493b0e65647e0335e6a7c4547abcea7df8e9
- https://git.kernel.org/stable/c/e8af3632a7f2da83e27b083f787bced1faba00b1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21758.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21758
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
