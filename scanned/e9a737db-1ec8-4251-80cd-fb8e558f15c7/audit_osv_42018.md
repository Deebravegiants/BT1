# [H] bpf: Validate BTF repeated field counts before expansion

## Summary
Severity: High
Advisory: CVE-2026-64354
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64354
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Validate BTF repeated field counts before expansion

btf_parse_struct_metas() walks user-supplied BTF during BPF_BTF_LOAD,
and btf_repeat_fields() expands repeatable fields from array elements
into the fixed BTF_FIELDS_MAX scratch array used by btf_parse_fields().

The remaining-capacity check performs the expanded field count calculation
in u32. A malformed BTF can wrap that calculation, causing the check to
pass even when the expanded field count exceeds the scratch array
capacity. The following memcpy() can then write past the end of the
array.

Use checked addition and multiplication before copying repeated fields
and reject impossible counts.

## References
- https://git.kernel.org/stable/c/b9452b594fd3aecbfd4aa0a6a1f741330a37dab7
- https://git.kernel.org/stable/c/c5ff816d5f13900c3f1f3298cfcc61339e056e56
- https://git.kernel.org/stable/c/cd407de2ef5dc70f1970b343ffaa16186340fdfd
- https://git.kernel.org/stable/c/ff77d013b737c0f77d925e2f2c59f0cf3d76bd35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64354.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64354
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
