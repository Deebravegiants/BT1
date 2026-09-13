# [M] CVE-2021-46917

## Summary
Severity: Medium
Advisory: CVE-2021-46917
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46917
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: fix wq cleanup of WQCFG registers

A pre-release silicon erratum workaround where wq reset does not clear
WQCFG registers was leaked into upstream code. Use wq reset command
instead of blasting the MMIO region. This also address an issue where
we clobber registers in future devices.

## References
- https://git.kernel.org/stable/c/ea9aadc06a9f10ad20a90edc0a484f1147d88a7a
- https://git.kernel.org/stable/c/f7dc8f5619165e1fa3383d0c2519f502d9e2a1a9
- https://git.kernel.org/stable/c/e5eb9757fe4c2392e069246ae78badc573af1833
