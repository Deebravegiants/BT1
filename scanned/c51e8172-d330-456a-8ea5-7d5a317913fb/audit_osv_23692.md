# [H] ext4: avoid cycles in directory h-tree

## Summary
Severity: High
Advisory: CVE-2022-49343
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49343
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: avoid cycles in directory h-tree

A maliciously corrupted filesystem can contain cycles in the h-tree
stored inside a directory. That can easily lead to the kernel corrupting
tree nodes that were already verified under its hands while doing a node
split and consequently accessing unallocated memory. Fix the problem by
verifying traversed block numbers are unique.

## References
- https://git.kernel.org/stable/c/24b8206fec1db21d7e82f21f0b2ff5e5672cf5b3
- https://git.kernel.org/stable/c/3a3ce941645407cd0b0b7f01ad9e2ea3770f46cc
- https://git.kernel.org/stable/c/3ba733f879c2a88910744647e41edeefbc0d92b2
- https://git.kernel.org/stable/c/6084240bfc44bf265ab6ae7d96980469b05be0f1
- https://git.kernel.org/stable/c/b3ad9ff6f06c1dc6abf7437691c88ca3d6da3ac0
- https://git.kernel.org/stable/c/d5a16a6df2c16eaf4de04948553ef0089dee463f
- https://git.kernel.org/stable/c/e157c8f87e8fac112d6c955e69a60cdb9bc80a60
- https://git.kernel.org/stable/c/ff4cafa51762da3824881a9000ca421d4b78b138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49343.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49343
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
