# [H] ipv6: sr: fix invalid unregister error path

## Summary
Severity: High
Advisory: CVE-2024-38612
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38612
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: sr: fix invalid unregister error path

The error path of seg6_init() is wrong in case CONFIG_IPV6_SEG6_LWTUNNEL
is not defined. In that case if seg6_hmac_init() fails, the
genl_unregister_family() isn't called.

This issue exist since commit 46738b1317e1 ("ipv6: sr: add option to control
lwtunnel support"), and commit 5559cea2d5aa ("ipv6: sr: fix possible
use-after-free and null-ptr-deref") replaced unregister_pernet_subsys()
with genl_unregister_family() in this error path.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/00e6335329f23ac6cf3105931691674e28bc598c
- https://git.kernel.org/stable/c/10610575a3ac2a702bf5c57aa931beaf847949c7
- https://git.kernel.org/stable/c/160e9d2752181fcf18c662e74022d77d3164cd45
- https://git.kernel.org/stable/c/1a63730fb315bb1bab97edd69ff58ad45e04bb01
- https://git.kernel.org/stable/c/3398a40dccb88d3a7eef378247a023a78472db66
- https://git.kernel.org/stable/c/646cd236c55e2cb5f146fc41bbe4034c4af5b2a4
- https://git.kernel.org/stable/c/85a70ff1e572160f1eeb096ed48d09a1c9d4d89a
- https://git.kernel.org/stable/c/c04d6a914e890ccea4a9d11233009a2ee7978bf4
- https://git.kernel.org/stable/c/e77a3ec7ada84543e75722a1283785a6544de925
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38612.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38612
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
