# [M] CVE-2022-48303

## Summary
Severity: Medium
Advisory: CVE-2022-48303
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/CVE-2022-48303
Type: osv

## Details
GNU Tar through 1.34 has a one-byte out-of-bounds read that results in use of uninitialized memory for a conditional jump. Exploitation to change the flow of control has not been demonstrated. The issue occurs in from_header in list.c via a V7 archive in which mtime has approximately 11 whitespace characters.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CRY7VEL4AIG3GLIEVCTOXRZNSVYDYYUD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X5VQYCO52Z7GAVCLRYUITN7KXHLRZQS4/
- https://savannah.gnu.org/patch/?10307
- https://savannah.gnu.org/bugs/?62387
