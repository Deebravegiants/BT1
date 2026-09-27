# [M] ARM: cns3xxx: Fix refcount leak in cns3xxx_init

## Summary
Severity: Medium
Advisory: CVE-2022-49677
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49677
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ARM: cns3xxx: Fix refcount leak in cns3xxx_init

of_find_compatible_node() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/1ba904b6b16e08de5aed7c1349838d9cd0d178c5
- https://git.kernel.org/stable/c/45bebbc8cea7d586a6216dc62814bdb380b9b29b
- https://git.kernel.org/stable/c/68d4303bf59662b64bd555e2aa0518282d20aa4f
- https://git.kernel.org/stable/c/b8b84e01ca94e2e1f5492353e9c24dab520b2e5b
- https://git.kernel.org/stable/c/c980392af1473d6d5662f70d8089c8e6d85144a4
- https://git.kernel.org/stable/c/d1359e4129ad43e43972a28838b87291c51de23d
- https://git.kernel.org/stable/c/da3ee7cd2f15922ad88a7ca6deee2eafdc7cd214
- https://git.kernel.org/stable/c/dc5170aae24e04068fd5ea125d06c0ab51f48a27
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49677.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49677
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
