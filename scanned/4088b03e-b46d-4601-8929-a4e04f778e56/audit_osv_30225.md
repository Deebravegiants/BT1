# [H] bpf, arm64: Fix address emission with tag-based KASAN enabled

## Summary
Severity: High
Advisory: CVE-2024-50203
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50203
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, arm64: Fix address emission with tag-based KASAN enabled

When BPF_TRAMP_F_CALL_ORIG is enabled, the address of a bpf_tramp_image
struct on the stack is passed during the size calculation pass and
an address on the heap is passed during code generation. This may
cause a heap buffer overflow if the heap address is tagged because
emit_a64_mov_i64() will emit longer code than it did during the size
calculation pass. The same problem could occur without tag-based
KASAN if one of the 16-bit words of the stack address happened to
be all-ones during the size calculation pass. Fix the problem by
assuming the worst case (4 instructions) when calculating the size
of the bpf_tramp_image address emission.

## References
- https://git.kernel.org/stable/c/7db1a2121f3c7903b8e397392beec563c3d00950
- https://git.kernel.org/stable/c/9e80f366ebfdfafc685fe83a84c34f7ef01cbe88
- https://git.kernel.org/stable/c/a552e2ef5fd1a6c78267cd4ec5a9b49aa11bbb1c
- https://git.kernel.org/stable/c/f521c2a0c0c4585f36d912bf62c852b88682c4f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50203.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50203
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
