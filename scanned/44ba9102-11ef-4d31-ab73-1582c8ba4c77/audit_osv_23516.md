# [H] ep93xx: clock: Fix UAF in ep93xx_clk_register_gate()

## Summary
Severity: High
Advisory: CVE-2022-49047
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49047
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ep93xx: clock: Fix UAF in ep93xx_clk_register_gate()

arch/arm/mach-ep93xx/clock.c:154:2: warning: Use of memory after it is freed [clang-analyzer-unix.Malloc]
arch/arm/mach-ep93xx/clock.c:151:2: note: Taking true branch
if (IS_ERR(clk))
^
arch/arm/mach-ep93xx/clock.c:152:3: note: Memory is released
kfree(psc);
^~~~~~~~~~
arch/arm/mach-ep93xx/clock.c:154:2: note: Use of memory after it is freed
return &psc->hw;
^ ~~~~~~~~

## References
- https://git.kernel.org/stable/c/0f12166872da46c6b57ba2f1314bbf310b3bf017
- https://git.kernel.org/stable/c/3b68b08885217abd9c57ff9b3bb3eb173eee02a9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49047.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
