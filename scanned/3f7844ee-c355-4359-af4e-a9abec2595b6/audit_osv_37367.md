# [H] bpf: Fix unsound scalar forking in maybe_fork_scalars() for BPF_OR

## Summary
Severity: High
Advisory: CVE-2026-31413
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-12
Source: https://osv.dev/vulnerability/CVE-2026-31413
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.75 <6.12.80, >=6.18.16 <6.18.21, >=6.19.6 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix unsound scalar forking in maybe_fork_scalars() for BPF_OR

maybe_fork_scalars() is called for both BPF_AND and BPF_OR when the
source operand is a constant.  When dst has signed range [-1, 0], it
forks the verifier state: the pushed path gets dst = 0, the current
path gets dst = -1.

For BPF_AND this is correct: 0 & K == 0.
For BPF_OR this is wrong:    0 | K == K, not 0.

The pushed path therefore tracks dst as 0 when the runtime value is K,
producing an exploitable verifier/runtime divergence that allows
out-of-bounds map access.

Fix this by passing env->insn_idx (instead of env->insn_idx + 1) to
push_stack(), so the pushed path re-executes the ALU instruction with
dst = 0 and naturally computes the correct result for any opcode.

## References
- https://git.kernel.org/stable/c/342aa1ee995ef5bbf876096dc3a5e51218d76fa4
- https://git.kernel.org/stable/c/58bd87d0e69204dbd739e4387a1edb0c4b1644e7
- https://git.kernel.org/stable/c/c845894ebd6fb43226b3118d6b017942550910c5
- https://git.kernel.org/stable/c/d13281ae7ea8902b21d99d10a2c8caf0bdec0455
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
