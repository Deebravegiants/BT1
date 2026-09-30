# [H] sh: intc: Fix use-after-free bug in register_intc_controller()

## Summary
Severity: High
Advisory: CVE-2024-53165
Ecosystem: Linux
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53165
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

sh: intc: Fix use-after-free bug in register_intc_controller()

In the error handling for this function, d is freed without ever
removing it from intc_list which would lead to a use after free.
To fix this, let's only add it to the list after everything has
succeeded.

## References
- https://git.kernel.org/stable/c/3c7c806b3eafd94ae0f77305a174d63b69ec187c
- https://git.kernel.org/stable/c/588bdec1ff8b81517dbae0ae51c9df52c0b952d3
- https://git.kernel.org/stable/c/63e72e551942642c48456a4134975136cdcb9b3c
- https://git.kernel.org/stable/c/6ba6e19912570b2ad68298be0be1dc779014a303
- https://git.kernel.org/stable/c/971b4893457788e0e123ea552f0bb126a5300e61
- https://git.kernel.org/stable/c/b8b84dcdf3ab1d414304819f824b10efba64132c
- https://git.kernel.org/stable/c/c3f4f4547fb291982f5ef56c048277c4d5ccc4e4
- https://git.kernel.org/stable/c/c43df7dae28fb9fce96ef088250c1e3c3a77c527
- https://git.kernel.org/stable/c/d8de818df12d86a1a26a8efd7b4b3b9c6dc3c5cc
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53165.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53165
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
