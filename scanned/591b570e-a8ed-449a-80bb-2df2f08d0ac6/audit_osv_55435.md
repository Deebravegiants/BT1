# [C] CVE-2025-47814

## Summary
Severity: Critical
Advisory: CVE-2025-47814
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-10
Source: https://osv.dev/vulnerability/CVE-2025-47814
Type: osv

## Details
libpspp-core.a in GNU PSPP through 2.0.1 allows attackers to cause a heap-based buffer overflow in inflate_read (called indirectly from spv_read_xml_member) in zip-reader.c.

## References
- https://savannah.gnu.org/bugs/?67074
