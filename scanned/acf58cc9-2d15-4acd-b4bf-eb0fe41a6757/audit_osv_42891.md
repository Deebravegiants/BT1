# [H] bpf: Reset register bounds before narrowing retval range in check_mem_access()

## Summary
Severity: High
Advisory: CVE-2026-72111
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72111
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.103, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reset register bounds before narrowing retval range in check_mem_access()

When the BPF verifier processes a context load of an LSM hook return
value, it calls __mark_reg_s32_range() to narrow the register to the
hook's valid range. However, __mark_reg_s32_range() intersects the new
range with the register's existing bounds using max_t()/min_t() rather
than replacing them.

If the destination register carries stale bounds from a prior instruction
(e.g. BPF_MOV64_IMM), the intersection can produce a range narrower than
reality. The verifier then believes it knows the register's exact value,
while at runtime the actual hook return value is loaded, creating a
verifier/runtime mismatch that can be used to bypass BPF memory safety
checks.

The else branch already calls mark_reg_unknown() to reset register state
before any narrowing. Apply the same reset in the is_retval path so
stale bounds are cleared before __mark_reg_s32_range() intersects.

## References
- https://git.kernel.org/stable/c/0993dc5fc619c0b25ab1310cb11d65e78351c0fe
- https://git.kernel.org/stable/c/5a55f9aecc08990940e70f0c7048a80850c5a16a
- https://git.kernel.org/stable/c/5e0b273e0a62cc04ec338c7b502797c66c2ed42a
- https://git.kernel.org/stable/c/bde92f65042ec14389782dd223f706bf6b59ce5d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72111.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72111
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
