# [H] LoongArch: BPF: Don't override subprog's return value

## Summary
Severity: High
Advisory: CVE-2025-22048
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22048
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: BPF: Don't override subprog's return value

The verifier test `calls: div by 0 in subprog` triggers a panic at the
ld.bu instruction. The ld.bu insn is trying to load byte from memory
address returned by the subprog. The subprog actually set the correct
address at the a5 register (dedicated register for BPF return values).
But at commit 73c359d1d356 ("LoongArch: BPF: Sign-extend return values")
we also sign extended a5 to the a0 register (return value in LoongArch).
For function call insn, we later propagate the a0 register back to a5
register. This is right for native calls but wrong for bpf2bpf calls
which expect zero-extended return value in a5 register. So only move a0
to a5 for native calls (i.e. non-BPF_PSEUDO_CALL).

## References
- https://git.kernel.org/stable/c/223d565d8892481684091cfbaf3466f2b0e289d3
- https://git.kernel.org/stable/c/60f3caff1492e5b8616b9578c4bedb5c0a88ed14
- https://git.kernel.org/stable/c/780628a780b622759d9e5adc76d15432144da1a3
- https://git.kernel.org/stable/c/7df2696256a034405d3c5a71b3a4c54725de4404
- https://git.kernel.org/stable/c/996e90ab446641553e8e21707b38b9709605e0e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22048.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22048
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
