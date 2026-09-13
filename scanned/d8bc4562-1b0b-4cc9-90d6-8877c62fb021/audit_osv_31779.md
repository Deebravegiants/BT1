# [H] ndisc: use RCU protection in ndisc_alloc_skb()

## Summary
Severity: High
Advisory: CVE-2025-21764
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21764
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ndisc: use RCU protection in ndisc_alloc_skb()

ndisc_alloc_skb() can be called without RTNL or RCU being held.

Add RCU protection to avoid possible UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/3c2d705f5adf5d860aaef90cb4211c0fde2ba66d
- https://git.kernel.org/stable/c/628e6d18930bbd21f2d4562228afe27694f66da9
- https://git.kernel.org/stable/c/96fc896d0e5b37c12808df797397fb16f3080879
- https://git.kernel.org/stable/c/9e0ec817eb41a55327a46cd3ce331a9868d60304
- https://git.kernel.org/stable/c/b870256dd2a5648d5ed2f22316b3ac29a7e5ed63
- https://git.kernel.org/stable/c/bbec88e4108e8d6fb468d3817fa652140a44ff28
- https://git.kernel.org/stable/c/c30893ef3d9cde8e7e8e4fd06b53d2c935bbccb1
- https://git.kernel.org/stable/c/cd1065f92eb7ff21b9ba5308a86f33d1670bf926
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21764.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21764
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
