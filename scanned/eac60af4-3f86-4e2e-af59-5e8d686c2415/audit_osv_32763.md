# [H] LoongArch: BPF: Fix off-by-one error in build_prologue()

## Summary
Severity: High
Advisory: CVE-2025-37893
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-18
Source: https://osv.dev/vulnerability/CVE-2025-37893
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: BPF: Fix off-by-one error in build_prologue()

Vincent reported that running BPF progs with tailcalls on LoongArch
causes kernel hard lockup. Debugging the issues shows that the JITed
image missing a jirl instruction at the end of the epilogue.

There are two passes in JIT compiling, the first pass set the flags and
the second pass generates JIT code based on those flags. With BPF progs
mixing bpf2bpf and tailcalls, build_prologue() generates N insns in the
first pass and then generates N+1 insns in the second pass. This makes
epilogue_offset off by one and we will jump to some unexpected insn and
cause lockup. Fix this by inserting a nop insn.

## References
- https://git.kernel.org/stable/c/205a2182c51ffebaef54d643e3745e720cded08b
- https://git.kernel.org/stable/c/48b904de2408af5f936f0e03f48dfcddeab58aa0
- https://git.kernel.org/stable/c/7e2586991e36663c9bc48c828b83eab180ad30a9
- https://git.kernel.org/stable/c/b3ffad2f02db4aace6799fe0049508b8925eae45
- https://git.kernel.org/stable/c/c74d95a5679741ef428974ab788f5b0758dc78ae
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37893.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37893
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
