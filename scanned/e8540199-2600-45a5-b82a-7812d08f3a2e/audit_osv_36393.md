# [H] bpf, arm64: Force 8-byte alignment for JIT buffer to prevent atomic tearing

## Summary
Severity: High
Advisory: CVE-2026-23383
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-23383
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.12.77, >=6.13.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, arm64: Force 8-byte alignment for JIT buffer to prevent atomic tearing

struct bpf_plt contains a u64 target field. Currently, the BPF JIT
allocator requests an alignment of 4 bytes (sizeof(u32)) for the JIT
buffer.

Because the base address of the JIT buffer can be 4-byte aligned (e.g.,
ending in 0x4 or 0xc), the relative padding logic in build_plt() fails
to ensure that target lands on an 8-byte boundary.

This leads to two issues:
1. UBSAN reports misaligned-access warnings when dereferencing the
   structure.
2. More critically, target is updated concurrently via WRITE_ONCE() in
   bpf_arch_text_poke() while the JIT'd code executes ldr. On arm64,
   64-bit loads/stores are only guaranteed to be single-copy atomic if
   they are 64-bit aligned. A misaligned target risks a torn read,
   causing the JIT to jump to a corrupted address.

Fix this by increasing the allocation alignment requirement to 8 bytes
(sizeof(u64)) in bpf_jit_binary_pack_alloc(). This anchors the base of
the JIT buffer to an 8-byte boundary, allowing the relative padding math
in build_plt() to correctly align the target field.

## References
- https://git.kernel.org/stable/c/519b1ad91de5bf7a496f2b858e9212db6328e1de
- https://git.kernel.org/stable/c/66959ed481a474eaae278c7f6860a2a9b188a4d6
- https://git.kernel.org/stable/c/80ad264da02cc4aee718e799c2b79f0f834673dc
- https://git.kernel.org/stable/c/ef06fd16d48704eac868441d98d4ef083d8f3d07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
