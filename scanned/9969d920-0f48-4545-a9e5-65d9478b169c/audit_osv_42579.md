# [H] bpf: Reject negative const offsets for buffer pointers

## Summary
Severity: High
Advisory: CVE-2026-68462
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68462
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject negative const offsets for buffer pointers

The verifier rejects variable offsets for PTR_TO_TP_BUFFER and PTR_TO_BUF
accesses, but it currently accepts a constant negative offset produced by
pointer arithmetic.

Commit 022ac0750883 ("bpf: use reg->var_off instead of reg->off for
pointers") moved constant pointer offsets from reg->off to reg->var_off.
However, __check_buffer_access() continued to check only the instruction
offset. An access with reg->var_off equal to -8 and an instruction offset
of zero therefore passes verification.

For writable raw tracepoints, the access end is also calculated from the
unsigned reg->var_off.value. An eight-byte access starting at -8 wraps
the calculated end to zero, allowing the program to load and attach
without increasing max_tp_access.

After ensuring that reg->var_off is constant, calculate the effective
access start using signed arithmetic and reject it when it is negative.
Use the validated start to calculate the access end for both
PTR_TO_TP_BUFFER and PTR_TO_BUF.

## References
- https://git.kernel.org/stable/c/314bd592085c0720ef519f6edbc5f41440ff78d4
- https://git.kernel.org/stable/c/fd4cfa8c8f9a17cdec0539334d28754bc1d8a5d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68462.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
