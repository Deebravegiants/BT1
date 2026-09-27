# [H] bpf, x86: fix freeing of not-finalized bpf_prog_pack

## Summary
Severity: High
Advisory: CVE-2022-50168
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50168
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, x86: fix freeing of not-finalized bpf_prog_pack

syzbot reported a few issues with bpf_prog_pack [1], [2]. This only happens
with multiple subprogs. In jit_subprogs(), we first call bpf_int_jit_compile()
on each sub program. And then, we call it on each sub program again. jit_data
is not freed in the first call of bpf_int_jit_compile(). Similarly we don't
call bpf_jit_binary_pack_finalize() in the first call of bpf_int_jit_compile().

If bpf_int_jit_compile() failed for one sub program, we will call
bpf_jit_binary_pack_finalize() for this sub program. However, we don't have a
chance to call it for other sub programs. Then we will hit "goto out_free" in
jit_subprogs(), and call bpf_jit_free on some subprograms that haven't got
bpf_jit_binary_pack_finalize() yet.

At this point, bpf_jit_binary_pack_free() is called and the whole 2MB page is
freed erroneously.

Fix this with a custom bpf_jit_free() for x86_64, which calls
bpf_jit_binary_pack_finalize() if necessary. Also, with custom
bpf_jit_free(), bpf_prog_aux->use_bpf_prog_pack is not needed any more,
remove it.

[1] https://syzkaller.appspot.com/bug?extid=2f649ec6d2eea1495a8f
[2] https://syzkaller.appspot.com/bug?extid=87f65c75f4a72db05445

## References
- https://git.kernel.org/stable/c/1d5f82d9dd477d5c66e0214a68c3e4f308eadd6d
- https://git.kernel.org/stable/c/60e66074812dde9cde3d99cdd3caa9e40f1a4516
- https://git.kernel.org/stable/c/f91ce608a79c0db3e72bd63c23e011a9ebc31505
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50168.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
