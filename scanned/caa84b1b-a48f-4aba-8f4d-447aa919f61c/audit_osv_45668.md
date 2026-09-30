# [M] JLSEC-2026-184

## Summary
Severity: Medium
Advisory: JLSEC-2026-184
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/JLSEC-2026-184
Type: osv

## Affected
- Julia: `Tar_jll` — affected >=0 <1.35.0+0

## Details
GNU Tar through 1.34 has a one-byte out-of-bounds read that results in use of uninitialized memory for a conditional jump. Exploitation to change the flow of control has not been demonstrated. The issue occurs in `from_header` in list.c via a V7 archive in which mtime has approximately 11 whitespace characters.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CRY7VEL4AIG3GLIEVCTOXRZNSVYDYYUD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X5VQYCO52Z7GAVCLRYUITN7KXHLRZQS4/
- https://savannah.gnu.org/bugs/?62387
- https://savannah.gnu.org/patch/?10307
