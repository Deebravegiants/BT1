# [H] bpf: Reject negative offsets for ALU ops

## Summary
Severity: High
Advisory: CVE-2025-40169
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40169
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject negative offsets for ALU ops

When verifying BPF programs, the check_alu_op() function validates
instructions with ALU operations. The 'offset' field in these
instructions is a signed 16-bit integer.

The existing check 'insn->off > 1' was intended to ensure the offset is
either 0, or 1 for BPF_MOD/BPF_DIV. However, because 'insn->off' is
signed, this check incorrectly accepts all negative values (e.g., -1).

This commit tightens the validation by changing the condition to
'(insn->off != 0 && insn->off != 1)'. This ensures that any value
other than the explicitly permitted 0 and 1 is rejected, hardening the
verifier against malformed BPF programs.

## References
- https://git.kernel.org/stable/c/21167bf70dbe400563e189ac632258d35eda38b5
- https://git.kernel.org/stable/c/3bce44b344040e5eef3d64d38b157c15304c0aab
- https://git.kernel.org/stable/c/5017c302ca4b2a45149ad64e058fa2d5623c068f
- https://git.kernel.org/stable/c/55c0ced59fe17dee34e9dfd5f7be63cbab207758
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40169.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40169
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
