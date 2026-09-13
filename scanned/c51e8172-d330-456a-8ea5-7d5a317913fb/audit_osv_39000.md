# [H] bpf: Properly mark live registers for indirect jumps

## Summary
Severity: High
Advisory: CVE-2026-43321
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43321
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Properly mark live registers for indirect jumps

For a `gotox rX` instruction the rX register should be marked as used
in the compute_insn_live_regs() function. Fix this.

## References
- https://git.kernel.org/stable/c/7beae54111c34ca63357ef120e115889b915beb5
- https://git.kernel.org/stable/c/d1aab1ca576c90192ba961094d51b0be6355a4d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43321.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43321
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
