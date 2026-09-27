# [H] icmp: prevent possible NULL dereferences from icmp_build_probe()

## Summary
Severity: High
Advisory: CVE-2024-35857
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35857
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.158, >=5.16.0 <6.1.90, >=6.2.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

icmp: prevent possible NULL dereferences from icmp_build_probe()

First problem is a double call to __in_dev_get_rcu(), because
the second one could return NULL.

if (__in_dev_get_rcu(dev) && __in_dev_get_rcu(dev)->ifa_list)

Second problem is a read from dev->ip6_ptr with no NULL check:

if (!list_empty(&rcu_dereference(dev->ip6_ptr)->addr_list))

Use the correct RCU API to fix these.

v2: add missing include <net/addrconf.h>

## References
- https://git.kernel.org/stable/c/23b7ee4a8d559bf38eac7ce5bb2f6ebf76f9c401
- https://git.kernel.org/stable/c/3e2979bf080c40da4f7c93aff8575ab8bc62b767
- https://git.kernel.org/stable/c/599c9ad5e1d43f5c12d869f5fd406ba5d8c55270
- https://git.kernel.org/stable/c/c58e88d49097bd12dfcfef4f075b43f5d5830941
- https://git.kernel.org/stable/c/d68dc711d84fdcf698e5d45308c3ddeede586350
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35857.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35857
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
