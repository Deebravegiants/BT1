# [H] bpf, arm64: Fix off-by-one in check_imm signed range check

## Summary
Severity: High
Advisory: CVE-2026-53036
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53036
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, arm64: Fix off-by-one in check_imm signed range check

check_imm(bits, imm) is used in the arm64 BPF JIT to verify that
a branch displacement (in arm64 instruction units) fits into the
signed N-bit immediate field of a B, B.cond or CBZ/CBNZ encoding
before it is handed to the encoder. The macro currently tests for
(imm > 0 && imm >> bits) || (imm < 0 && ~imm >> bits) which admits
values in [-2^N, 2^N) — effectively a signed (N+1)-bit range. A
signed N-bit field only holds [-2^(N-1), 2^(N-1)), so the check
admits one extra bit of range on each side.

In particular, for check_imm19(), values in [2^18, 2^19) slip past
the check but do not fit into the 19-bit signed imm19 field of
B.cond. aarch64_insn_encode_immediate() then masks the raw value
into the 19-bit field, setting bit 18 (the sign bit) and flipping
a forward branch into a backward one. Same class of issue exists
for check_imm26() and the B/BL encoding. Shift by (bits - 1)
instead of bits so the actual signed N-bit range is enforced.

## References
- https://git.kernel.org/stable/c/1a113b5497297871699cd498b1b83542e0db7f15
- https://git.kernel.org/stable/c/1dd8be4ec722ce54e4cace59f3a4ba658111b3ec
- https://git.kernel.org/stable/c/6927f0d6794aa73318bbfa929f1ff6065b0620df
- https://git.kernel.org/stable/c/7fd3b41260c6120e7b60164afea5d961af6224f9
- https://git.kernel.org/stable/c/a5dfeb3b61065039488342d43ae06d4729d955d4
- https://git.kernel.org/stable/c/fb74defa1cca1a73177c0c761e641332e4f979a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53036.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
