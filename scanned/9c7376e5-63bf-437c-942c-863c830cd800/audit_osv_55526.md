# [H] CVE-2025-65411

## Summary
Severity: High
Advisory: CVE-2025-65411
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2025-65411
Type: osv

## Details
A NULL pointer dereference in the src/path.c component of GNU Unrtf v0.21.10 allows attackers to cause a Denial of Service (DoS) via injecting a crafted payload into the search_path parameter.

## References
- https://savannah.gnu.org/projects/unrtf/
- https://sources.debian.org/src/unrtf/0.21.10-clean-1/src/main.c/#L661
- https://www.gnu.org/software/unrtf/
- https://lists.gnu.org/archive/html/bug-unrtf/2025-11/msg00000.html
- https://github.com/MAXEUR5/Vulnerability_Disclosures/blob/main/2025/CVE-2025-65411.md
