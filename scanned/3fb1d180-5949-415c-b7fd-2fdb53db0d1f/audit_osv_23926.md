# [M] xtensa: xtfpga: Fix refcount leak bug in setup

## Summary
Severity: Medium
Advisory: CVE-2022-49681
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49681
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.9.321, >=4.10.0 <4.14.286, >=4.15.0 <4.19.250, >=4.20.0 <5.4.202, >=5.5.0 <5.10.127, >=5.11.0 <5.15.51, >=5.16.0 <5.18.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

xtensa: xtfpga: Fix refcount leak bug in setup

In machine_setup(), of_find_compatible_node() will return a node
pointer with refcount incremented. We should use of_node_put() when
it is not used anymore.

## References
- https://git.kernel.org/stable/c/0162451723178602c37f0555d235dfa17e486112
- https://git.kernel.org/stable/c/0715d0e60052662c3f225342062f174dd721d1c7
- https://git.kernel.org/stable/c/173940b3ae40114d4179c251a98ee039dc9cd5b3
- https://git.kernel.org/stable/c/35d7e961be68732eb3acaeba81fb81ca16eafd05
- https://git.kernel.org/stable/c/6c0839cf1b9e1b3c88da6af76794583cbfae8da3
- https://git.kernel.org/stable/c/9b30c5c8884eda3f541229899671cebbad15979b
- https://git.kernel.org/stable/c/a52972ee706b438302eb0350e61f378eb191e3d1
- https://git.kernel.org/stable/c/b12d5c52f073a0420622aaf2f21b615cce8b36cc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49681.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49681
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
