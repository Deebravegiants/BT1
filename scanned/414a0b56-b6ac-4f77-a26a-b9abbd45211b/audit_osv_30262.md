# [H] bpf: Check the validity of nr_words in bpf_iter_bits_new()

## Summary
Severity: High
Advisory: CVE-2024-50253
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50253
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Check the validity of nr_words in bpf_iter_bits_new()

Check the validity of nr_words in bpf_iter_bits_new(). Without this
check, when multiplication overflow occurs for nr_bits (e.g., when
nr_words = 0x0400-0001, nr_bits becomes 64), stack corruption may occur
due to bpf_probe_read_kernel_common(..., nr_bytes = 0x2000-0008).

Fix it by limiting the maximum value of nr_words to 511. The value is
derived from the current implementation of BPF memory allocator. To
ensure compatibility if the BPF memory allocator's size limitation
changes in the future, use the helper bpf_mem_alloc_check_size() to
check whether nr_bytes is too larger. And return -E2BIG instead of
-ENOMEM for oversized nr_bytes.

## References
- https://git.kernel.org/stable/c/393397fbdcad7396639d7077c33f86169184ba99
- https://git.kernel.org/stable/c/c9539e09c67880ecd88b51188c346a2cc078b06c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50253.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50253
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
