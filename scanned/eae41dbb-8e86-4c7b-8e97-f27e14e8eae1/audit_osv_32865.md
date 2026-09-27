# [H] arm64/fpsimd: Avoid clobbering kernel FPSIMD state with SMSTOP

## Summary
Severity: High
Advisory: CVE-2025-38169
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38169
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64/fpsimd: Avoid clobbering kernel FPSIMD state with SMSTOP

On system with SME, a thread's kernel FPSIMD state may be erroneously
clobbered during a context switch immediately after that state is
restored. Systems without SME are unaffected.

If the CPU happens to be in streaming SVE mode before a context switch
to a thread with kernel FPSIMD state, fpsimd_thread_switch() will
restore the kernel FPSIMD state using fpsimd_load_kernel_state() while
the CPU is still in streaming SVE mode. When fpsimd_thread_switch()
subsequently calls fpsimd_flush_cpu_state(), this will execute an
SMSTOP, causing an exit from streaming SVE mode. The exit from
streaming SVE mode will cause the hardware to reset a number of
FPSIMD/SVE/SME registers, clobbering the FPSIMD state.

Fix this by calling fpsimd_flush_cpu_state() before restoring the kernel
FPSIMD state.

## References
- https://git.kernel.org/stable/c/01098d893fa8a6edb2b56e178b798e3e6b674f02
- https://git.kernel.org/stable/c/55d52af498daea75aa03ba9b7e444c8ae495ac20
- https://git.kernel.org/stable/c/a305821f597ec943849d3e53924adb88c61ed682
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38169.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38169
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
