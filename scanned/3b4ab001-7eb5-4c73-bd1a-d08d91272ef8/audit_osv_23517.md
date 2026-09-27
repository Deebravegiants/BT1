# [H] ipv6: fix panic when forwarding a pkt with no in6 dev

## Summary
Severity: High
Advisory: CVE-2022-49048
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49048
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.239, >=4.20.0 <5.4.190, >=5.5.0 <5.10.112, >=5.11.0 <5.15.35, >=5.14.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix panic when forwarding a pkt with no in6 dev

kongweibin reported a kernel panic in ip6_forward() when input interface
has no in6 dev associated.

The following tc commands were used to reproduce this panic:
tc qdisc del dev vxlan100 root
tc qdisc add dev vxlan100 root netem corrupt 5%

## References
- https://git.kernel.org/stable/c/74b68f5249f16c5f7f675d0f604fa6ae20e3a151
- https://git.kernel.org/stable/c/a263712ba8c9ded25dd9d2d5ced11bcea5b33a3e
- https://git.kernel.org/stable/c/ab2f5afb7af5c68389e8c7dd29e0a98fbeaaa435
- https://git.kernel.org/stable/c/adee01bbf6cb5b3e4ed08be8ff866aac90f13836
- https://git.kernel.org/stable/c/e3fa461d8b0e185b7da8a101fe94dfe6dd500ac0
- https://git.kernel.org/stable/c/e69fb3de87a8923e5931a272a38fa3cceb01da44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49048.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
