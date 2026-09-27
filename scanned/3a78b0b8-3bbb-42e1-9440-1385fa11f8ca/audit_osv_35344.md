# [H] MIPS: ftrace: Fix memory corruption when kernel is located beyond 32 bits

## Summary
Severity: High
Advisory: CVE-2025-71109
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71109
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <6.12.64, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

MIPS: ftrace: Fix memory corruption when kernel is located beyond 32 bits

Since commit e424054000878 ("MIPS: Tracing: Reduce the overhead of
dynamic Function Tracer"), the macro UASM_i_LA_mostly has been used,
and this macro can generate more than 2 instructions. At the same
time, the code in ftrace assumes that no more than 2 instructions can
be generated, which is why it stores them in an int[2] array. However,
as previously noted, the macro UASM_i_LA_mostly (and now UASM_i_LA)
causes a buffer overflow when _mcount is beyond 32 bits. This leads to
corruption of the variables located in the __read_mostly section.

This corruption was observed because the variable
__cpu_primary_thread_mask was corrupted, causing a hang very early
during boot.

This fix prevents the corruption by avoiding the generation of
instructions if they could exceed 2 instructions in
length. Fortunately, insn_la_mcount is only used if the instrumented
code is located outside the kernel code section, so dynamic ftrace can
still be used, albeit in a more limited scope. This is still
preferable to corrupting memory and/or crashing the kernel.

## References
- https://git.kernel.org/stable/c/36dac9a3dda1f2bae343191bc16b910c603cac25
- https://git.kernel.org/stable/c/7f39b9d0e86ed6236b9a5fb67616ab1f76c4f150
- https://git.kernel.org/stable/c/e3e33ac2eb69d595079a1a1e444c2fb98efdd42d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71109.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71109
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
