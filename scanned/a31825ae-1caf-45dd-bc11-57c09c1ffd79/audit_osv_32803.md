# [H] can: bcm: add missing rcu read protection for procfs content

## Summary
Severity: High
Advisory: CVE-2025-38003
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-08
Source: https://osv.dev/vulnerability/CVE-2025-38003
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=5.19.0 <6.6.93, >=6.2.0 <6.12.31, >=6.7.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: add missing rcu read protection for procfs content

When the procfs content is generated for a bcm_op which is in the process
to be removed the procfs output might show unreliable data (UAF).

As the removal of bcm_op's is already implemented with rcu handling this
patch adds the missing rcu_read_lock() and makes sure the list entries
are properly removed under rcu protection.

## References
- https://git.kernel.org/stable/c/0622846db728a5332b917c797c733e202c4620ae
- https://git.kernel.org/stable/c/19f553a1ddf260da6570ed8f8d91a8c87f49b63a
- https://git.kernel.org/stable/c/1f912f8484e9c4396378c39460bbea0af681f319
- https://git.kernel.org/stable/c/63567ecd99a24495208dc860d50fb17440043006
- https://git.kernel.org/stable/c/659701c0b954ccdb4a916a4ad59bbc16e726d42c
- https://git.kernel.org/stable/c/6d7d458c41b98a5c1670cbd36f2923c37de51cf5
- https://git.kernel.org/stable/c/7c9db92d5f0eadca30884af75c53d601edc512ee
- https://git.kernel.org/stable/c/dac5e6249159ac255dad9781793dbe5908ac9ddb
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38003.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
