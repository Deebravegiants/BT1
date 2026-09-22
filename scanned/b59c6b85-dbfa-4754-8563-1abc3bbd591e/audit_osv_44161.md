# [H] clk: spacemit: k3: set hdma clock as critical

## Summary
Severity: High
Advisory: CVE-2026-80523
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80523
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: spacemit: k3: set hdma clock as critical

HDMA clock is responsible for the internal TCM access path of X100 RISC-V
core, so set the clock flag as critical to prevent it from being shut off,
otherwise the Linux system will hang, for example in the case of a vector
instruction access generates a page fault.

## References
- https://git.kernel.org/stable/c/bb81b608db6342e5adccb6aabe900d739dc7cddb
- https://git.kernel.org/stable/c/eb525edd48907795c0d4e498ff57ad168070b289
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80523.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80523
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
