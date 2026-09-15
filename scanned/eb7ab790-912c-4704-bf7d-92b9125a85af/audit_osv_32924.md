# [H] powerpc/bpf: fix JIT code size calculation of bpf trampoline

## Summary
Severity: High
Advisory: CVE-2025-38339
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38339
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/bpf: fix JIT code size calculation of bpf trampoline

arch_bpf_trampoline_size() provides JIT size of the BPF trampoline
before the buffer for JIT'ing it is allocated. The total number of
instructions emitted for BPF trampoline JIT code depends on where
the final image is located. So, the size arrived at with the dummy
pass in arch_bpf_trampoline_size() can vary from the actual size
needed in  arch_prepare_bpf_trampoline().  When the instructions
accounted in  arch_bpf_trampoline_size() is less than the number of
instructions emitted during the actual JIT compile of the trampoline,
the below warning is produced:

  WARNING: CPU: 8 PID: 204190 at arch/powerpc/net/bpf_jit_comp.c:981 __arch_prepare_bpf_trampoline.isra.0+0xd2c/0xdcc

which is:

  /* Make sure the trampoline generation logic doesn't overflow */
  if (image && WARN_ON_ONCE(&image[ctx->idx] >
  			(u32 *)rw_image_end - BPF_INSN_SAFETY)) {

So, during the dummy pass, instead of providing some arbitrary image
location, account for maximum possible instructions if and when there
is a dependency with image location for JIT'ing.

## References
- https://git.kernel.org/stable/c/59ba025948be2a92e8bc9ae1cbdaf197660bd508
- https://git.kernel.org/stable/c/7833deb95e05bec146414b3a2feb24f025ca27c0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38339.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38339
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
