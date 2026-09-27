# [M] CVE-2025-65410

## Summary
Severity: Medium
Advisory: CVE-2025-65410
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-65410
Type: osv

## Details
A stack overflow in the src/main.c component of GNU Unrtf v0.21.10 allows attackers to cause a Denial of Service (DoS) via injecting a crafted input into the filename parameter.

## References
- https://www.gnu.org/software/unrtf/
- https://hg.savannah.gnu.org/hgweb/unrtf/rev/a5d3b025a8b1
- https://savannah.gnu.org/projects/unrtf/
- https://lists.gnu.org/archive/html/bug-unrtf/2025-11/msg00001.html
- https://github.com/MAXEUR5/Vulnerability_Disclosures/blob/main/2025/CVE-2025-65410.md
