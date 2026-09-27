# [C] ipv6: prevent possible UAF in ip6_xmit()

## Summary
Severity: Critical
Advisory: CVE-2024-44985
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44985
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.166, >=5.16.0 <6.1.107, >=6.2.0 <6.6.48, >=6.7.0 <6.10.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: prevent possible UAF in ip6_xmit()

If skb_expand_head() returns NULL, skb has been freed
and the associated dst/idev could also have been freed.

We must use rcu_read_lock() to prevent a possible UAF.

## References
- https://git.kernel.org/stable/c/124b428fe28064c809e4237b0b38e97200a8a4a8
- https://git.kernel.org/stable/c/2d5ff7e339d04622d8282661df36151906d0e1c7
- https://git.kernel.org/stable/c/38a21c026ed2cc7232414cb166efc1923f34af17
- https://git.kernel.org/stable/c/975f764e96f71616b530e300c1bb2ac0ce0c2596
- https://git.kernel.org/stable/c/b3a3d5333c13a1be57499581eab4a8fc94d57f36
- https://git.kernel.org/stable/c/c47e022011719fc5727bca661d662303180535ba
- https://git.kernel.org/stable/c/fc88d6c1f2895a5775795d82ec581afdff7661d1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44985.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
