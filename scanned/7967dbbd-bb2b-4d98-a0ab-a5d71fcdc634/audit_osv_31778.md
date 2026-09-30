# [H] neighbour: use RCU protection in __neigh_notify()

## Summary
Severity: High
Advisory: CVE-2025-21763
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21763
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

neighbour: use RCU protection in __neigh_notify()

__neigh_notify() can be called without RTNL or RCU protection.

Use RCU protection to avoid potential UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1cbb2aa90cd3fba15ad7efb5cdda28f3d1082379
- https://git.kernel.org/stable/c/40d8f2f2a373b6c294ffac394d2bb814b572ead1
- https://git.kernel.org/stable/c/559307d25235e24b5424778c7332451b6c741159
- https://git.kernel.org/stable/c/784eb2376270e086f7db136d154b8404edacf97b
- https://git.kernel.org/stable/c/8666e9aab801328c1408a19fbf4070609dc0695a
- https://git.kernel.org/stable/c/becbd5850c03ed33b232083dd66c6e38c0c0e569
- https://git.kernel.org/stable/c/cdd5c2a12ddad8a77ce1838ff9f29aa587de82df
- https://git.kernel.org/stable/c/e1aed6be381bcd7f46d4ca9d7ef0f5f3d6a1be32
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21763.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21763
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
