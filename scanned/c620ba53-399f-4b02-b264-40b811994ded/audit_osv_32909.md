# [H] net: tipc: fix refcount warning in tipc_aead_encrypt

## Summary
Severity: High
Advisory: CVE-2025-38273
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38273
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tipc: fix refcount warning in tipc_aead_encrypt

syzbot reported a refcount warning [1] caused by calling get_net() on
a network namespace that is being destroyed (refcount=0). This happens
when a TIPC discovery timer fires during network namespace cleanup.

The recently added get_net() call in commit e279024617134 ("net/tipc:
fix slab-use-after-free Read in tipc_aead_encrypt_done") attempts to
hold a reference to the network namespace. However, if the namespace
is already being destroyed, its refcount might be zero, leading to the
use-after-free warning.

Replace get_net() with maybe_get_net(), which safely checks if the
refcount is non-zero before incrementing it. If the namespace is being
destroyed, return -ENODEV early, after releasing the bearer reference.

[1]: https://lore.kernel.org/all/68342b55.a70a0220.253bc2.0091.GAE@google.com/T/#m12019cf9ae77e1954f666914640efa36d52704a2

## References
- https://git.kernel.org/stable/c/307391e8fe70401a6d39ecc9978e13c2c0cdf81f
- https://git.kernel.org/stable/c/445d59025d76d0638b03110f8791d5b89ed5162d
- https://git.kernel.org/stable/c/9ff60e0d9974dccf24e89bcd3ee7933e538d929f
- https://git.kernel.org/stable/c/acab7ca5ff19889b80a8ee7dec220ee1a96dede9
- https://git.kernel.org/stable/c/c762fc79d710d676b793f9d98b1414efe6eb51e6
- https://git.kernel.org/stable/c/e0b11227c4e8eb4bdf1b86aa8f0f3abb24e0f029
- https://git.kernel.org/stable/c/f29ccaa07cf3d35990f4d25028cc55470d29372b
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38273.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38273
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
