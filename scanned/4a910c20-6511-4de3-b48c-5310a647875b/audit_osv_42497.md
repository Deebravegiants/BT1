# [H] LoongArch: BPF: Zero-extend signed ALU32 div/mod results

## Summary
Severity: High
Advisory: CVE-2026-68295
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68295
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: BPF: Zero-extend signed ALU32 div/mod results

ALU32 operations write a 32-bit result and leave the upper 32 bits of
the BPF register zero. The LoongArch JIT sign-extends the result of
signed ALU32 BPF_DIV and BPF_MOD (off=1), so a negative 32-bit quotient
or remainder leaves bits 63:32 set in JITted code while the verifier
and interpreter model those bits as zero.

Keep sign-extension on the operands, which signed divide needs, and
zero-extend the ALU32 result after the divide or modulo instruction,
matching the unsigned ALU32 div/mod paths and every other ALU32
operation in this JIT.

## References
- https://git.kernel.org/stable/c/716cb29dbed4d62e9e108950a1a82bcba4cc2d45
- https://git.kernel.org/stable/c/dacd348b8a993373576fe2ee2d8b114740ba57a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68295.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68295
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
