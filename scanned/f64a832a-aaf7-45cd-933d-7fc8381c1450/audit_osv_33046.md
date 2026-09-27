# [H] net/packet: fix a race in packet_set_ring() and packet_notifier()

## Summary
Severity: High
Advisory: CVE-2025-38617
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38617
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/packet: fix a race in packet_set_ring() and packet_notifier()

When packet_set_ring() releases po->bind_lock, another thread can
run packet_notifier() and process an NETDEV_UP event.

This race and the fix are both similar to that of commit 15fe076edea7
("net/packet: fix a race in packet_bind() and packet_notifier()").

There too the packet_notifier NETDEV_UP event managed to run while a
po->bind_lock critical section had to be temporarily released. And
the fix was similarly to temporarily set po->num to zero to keep
the socket unhooked until the lock is retaken.

The po->bind_lock in packet_set_ring and packet_notifier precede the
introduction of git history.

## References
- https://git.kernel.org/stable/c/01d3c8417b9c1b884a8a981a3b886da556512f36
- https://git.kernel.org/stable/c/18f13f2a83eb81be349a9757ba2141ff1da9ad73
- https://git.kernel.org/stable/c/7da733f117533e9b2ebbd530a22ae4028713955c
- https://git.kernel.org/stable/c/7de07705007c7e34995a5599aaab1d23e762d7ca
- https://git.kernel.org/stable/c/88caf46db8239e6471413d28aabaa6b8bd552805
- https://git.kernel.org/stable/c/ba2257034755ae773722f15f4c3ad1dcdad15ca9
- https://git.kernel.org/stable/c/e50ccfaca9e3c671cae917dcb994831a859cf588
- https://git.kernel.org/stable/c/f1791fd7b845bea0ce9674fcf2febee7bc87a893
- https://git.kernel.org/stable/c/f2e8fcfd2b1bc754920108b7f2cd75082c5a18df
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38617.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38617
- https://github.com/google/security-research/pull/339
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://blog.calif.io/p/a-race-within-a-race-exploiting-cve
