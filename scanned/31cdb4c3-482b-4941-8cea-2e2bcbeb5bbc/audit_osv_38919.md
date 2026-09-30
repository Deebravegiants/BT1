# [H] bpf: Reset register ID for BPF_END value tracking

## Summary
Severity: High
Advisory: CVE-2026-43070
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-43070
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.17 <6.18.21, >=6.19.7 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reset register ID for BPF_END value tracking

When a register undergoes a BPF_END (byte swap) operation, its scalar
value is mutated in-place. If this register previously shared a scalar ID
with another register (e.g., after an `r1 = r0` assignment), this tie must
be broken.

Currently, the verifier misses resetting `dst_reg->id` to 0 for BPF_END.
Consequently, if a conditional jump checks the swapped register, the
verifier incorrectly propagates the learned bounds to the linked register,
leading to false confidence in the linked register's value and potentially
allowing out-of-bounds memory accesses.

Fix this by explicitly resetting `dst_reg->id` to 0 in the BPF_END case
to break the scalar tie, similar to how BPF_NEG handles it via
`__mark_reg_known`.

## References
- https://git.kernel.org/stable/c/0d15c3611a2cc5d08993545d4032055ae10ae2c1
- https://git.kernel.org/stable/c/a17443af874229408ce6b78e2c8a2b5adeb4b7d8
- https://git.kernel.org/stable/c/a3125bc01884431d30d731461634c8295b6f0529
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43070.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
