# [C] CVE-2025-47816

## Summary
Severity: Critical
Advisory: CVE-2025-47816
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-10
Source: https://osv.dev/vulnerability/CVE-2025-47816
Type: osv

## Details
libpspp-core.a in GNU PSPP through 2.0.1 allows attackers to cause an spvxml-helpers.c spvxml_parse_attributes out-of-bounds read, related to extra content at the end of a document.

## References
- https://savannah.gnu.org/bugs/?67073
