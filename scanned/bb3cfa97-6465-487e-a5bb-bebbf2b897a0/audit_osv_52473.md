# [H] CVE-2021-47486

## Summary
Severity: High
Advisory: CVE-2021-47486
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47486
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv, bpf: Fix potential NULL dereference

The bpf_jit_binary_free() function requires a non-NULL argument. When
the RISC-V BPF JIT fails to converge in NR_JIT_ITERATIONS steps,
jit_data->header will be NULL, which triggers a NULL
dereference. Avoid this by checking the argument, prior calling the
function.

## References
- https://git.kernel.org/stable/c/27de809a3d83a6199664479ebb19712533d6fd9b
- https://git.kernel.org/stable/c/cac6b043cea3e120f4fccec16f7381747cbfdc0d
- https://git.kernel.org/stable/c/e1b80a5ebe5431caeb20f88c32d4a024777a2d41
