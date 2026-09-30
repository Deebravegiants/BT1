# [H] bpf: Preserve pointer spill metadata during half-slot cleanup

## Summary
Severity: High
Advisory: CVE-2026-72426
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72426
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Preserve pointer spill metadata during half-slot cleanup

__clean_func_state() cleans dead stack slots in 4-byte halves. When the
high half of a STACK_SPILL slot is dead and the low half remains live,
cleanup converts the live low half to STACK_MISC or STACK_ZERO and clears
the saved spilled_ptr metadata.

That conversion is safe only for scalar spills. For a pointer spill, this
metadata clear lets a later 32-bit fill from the still-live half avoid the
normal non-scalar register-fill check and be treated as an ordinary scalar
stack read.

Leave non-scalar spill slots intact in this half-live shape. This is
conservative for pruning and preserves the existing
check_stack_read_fixed_off() rejection path for partial fills from pointer
spills.

## References
- https://git.kernel.org/stable/c/0f9278b22cda6fd2525049930157b79b4036b4ef
- https://git.kernel.org/stable/c/3a354149bceacadbcf7d7b4766f5ef26a85892ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72426.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72426
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
