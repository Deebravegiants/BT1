# [H] bpf: Fix undefined behavior in interpreter sdiv/smod for INT_MIN

## Summary
Severity: High
Advisory: CVE-2026-31525
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31525
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix undefined behavior in interpreter sdiv/smod for INT_MIN

The BPF interpreter's signed 32-bit division and modulo handlers use
the kernel abs() macro on s32 operands. The abs() macro documentation
(include/linux/math.h) explicitly states the result is undefined when
the input is the type minimum. When DST contains S32_MIN (0x80000000),
abs((s32)DST) triggers undefined behavior and returns S32_MIN unchanged
on arm64/x86. This value is then sign-extended to u64 as
0xFFFFFFFF80000000, causing do_div() to compute the wrong result.

The verifier's abstract interpretation (scalar32_min_max_sdiv) computes
the mathematically correct result for range tracking, creating a
verifier/interpreter mismatch that can be exploited for out-of-bounds
map value access.

Introduce abs_s32() which handles S32_MIN correctly by casting to u32
before negating, avoiding signed overflow entirely. Replace all 8
abs((s32)...) call sites in the interpreter's sdiv32/smod32 handlers.

s32 is the only affected case -- the s64 division/modulo handlers do
not use abs().

## References
- https://git.kernel.org/stable/c/0d5d8c3ce45c734aaf3c51cbef59155a6746157d
- https://git.kernel.org/stable/c/694ea55f1b1c74f9942d91ec366ae9e822422e42
- https://git.kernel.org/stable/c/9ab1227765c446942f290c83382f0b19887c55cf
- https://git.kernel.org/stable/c/c77b30bd1dcb61f66c640ff7d2757816210c7cb0
- https://git.kernel.org/stable/c/f14ca604c0ff274fba19f73f1f0485c0047c1396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31525.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31525
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
