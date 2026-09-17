# [H] net: mctp: Set SOCK_RCU_FREE

## Summary
Severity: High
Advisory: CVE-2025-37790
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37790
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mctp: Set SOCK_RCU_FREE

Bind lookup runs under RCU, so ensure that a socket doesn't go away in
the middle of a lookup.

## References
- https://git.kernel.org/stable/c/3f899bd6dd56ddc46509b526e23a8f0a97712a6d
- https://git.kernel.org/stable/c/52024cd6ec71a6ca934d0cc12452bd8d49850679
- https://git.kernel.org/stable/c/5c1313b93c8c2e3904a48aa88e2fa1db28c607ae
- https://git.kernel.org/stable/c/a8a3b61ce140e2b0a72a779e8d70f60c0cf1e47a
- https://git.kernel.org/stable/c/b9764ebebb007249fb733a131b6110ff333b6616
- https://git.kernel.org/stable/c/e3b5edbdb45924a7d4206d13868a2aac71f1e53d
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37790.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
