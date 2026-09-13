# [H] net/rds: Restrict use of RDS/IB to the initial network namespace

## Summary
Severity: High
Advisory: CVE-2026-53077
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53077
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/rds: Restrict use of RDS/IB to the initial network namespace

Prevent using RDS/IB in network namespaces other than the initial one.
The existing RDS/IB code will not work properly in non-initial network
namespaces.

## References
- https://git.kernel.org/stable/c/07035306bf722f4676a1aee35cbeb3732c76194e
- https://git.kernel.org/stable/c/3174fc703d081d2ca538b22fba734e3ad5b52322
- https://git.kernel.org/stable/c/3e7f14cd5a51533404e1ae4809caab46073fb5c7
- https://git.kernel.org/stable/c/a7494479757d60d2413bfaa087f8431a26eea032
- https://git.kernel.org/stable/c/b6a54f5e9ce9b97ae641855378d71c5154a085c0
- https://git.kernel.org/stable/c/c244b79adffad89a5173cf8bfaa06a6b40bbd09b
- https://git.kernel.org/stable/c/ebf71dd4aff46e8e421d455db3e231ba43d2fa8a
- https://git.kernel.org/stable/c/fb407343c0c16e94584707b2dfdd350a5f81b000
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53077.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53077
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
