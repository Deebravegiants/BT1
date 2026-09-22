# [H] bpf: Guard stack limits against 32bit overflow

## Summary
Severity: High
Advisory: CVE-2023-52676
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52676
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Guard stack limits against 32bit overflow

This patch promotes the arithmetic around checking stack bounds to be
done in the 64-bit domain, instead of the current 32bit. The arithmetic
implies adding together a 64-bit register with a int offset. The
register was checked to be below 1<<29 when it was variable, but not
when it was fixed. The offset either comes from an instruction (in which
case it is 16 bit), from another register (in which case the caller
checked it to be below 1<<29 [1]), or from the size of an argument to a
kfunc (in which case it can be a u32 [2]). Between the register being
inconsistently checked to be below 1<<29, and the offset being up to an
u32, it appears that we were open to overflowing the `int`s which were
currently used for arithmetic.

[1] https://github.com/torvalds/linux/blob/815fb87b753055df2d9e50f6cd80eb10235fe3e9/kernel/bpf/verifier.c#L7494-L7498
[2] https://github.com/torvalds/linux/blob/815fb87b753055df2d9e50f6cd80eb10235fe3e9/kernel/bpf/verifier.c#L11904

## References
- https://git.kernel.org/stable/c/1d38a9ee81570c4bd61f557832dead4d6f816760
- https://git.kernel.org/stable/c/ad140fc856f0b1d5e2215bcb6d0cc247a86805a2
- https://git.kernel.org/stable/c/e5ad9ecb84405637df82732ee02ad741a5f782a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52676.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
