# [H] openvswitch: Fix unsafe attribute parsing in output_userspace()

## Summary
Severity: High
Advisory: CVE-2025-37998
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2025-37998
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.183, >=5.16.0 <6.1.139, >=6.2.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

openvswitch: Fix unsafe attribute parsing in output_userspace()

This patch replaces the manual Netlink attribute iteration in
output_userspace() with nla_for_each_nested(), which ensures that only
well-formed attributes are processed.

## References
- https://git.kernel.org/stable/c/0236742bd959332181c1fcc41a05b7b709180501
- https://git.kernel.org/stable/c/06b4f110c79716c181a8c5da007c259807840232
- https://git.kernel.org/stable/c/47f7f00cf2fa3137d5c0416ef1a71bdf77901395
- https://git.kernel.org/stable/c/4fa672cbce9c86c3efb8621df1ae580d47813430
- https://git.kernel.org/stable/c/6712dc21506738f5f22b4f68b7c0d9e0df819dbd
- https://git.kernel.org/stable/c/6beb6835c1fbb3f676aebb51a5fee6b77fed9308
- https://git.kernel.org/stable/c/bca8df998cce1fead8cbc69144862eadc2e34c87
- https://git.kernel.org/stable/c/ec334aaab74705cc515205e1da3cb369fdfd93cd
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37998.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37998
- https://www.zerodayinitiative.com/advisories/ZDI-25-307/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
