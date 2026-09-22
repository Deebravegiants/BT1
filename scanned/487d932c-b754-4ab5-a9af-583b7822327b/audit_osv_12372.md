# [C] CVE-2018-11547

## Summary
Severity: Critical
Advisory: CVE-2018-11547
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-29
Source: https://osv.dev/vulnerability/CVE-2018-11547
Type: osv

## Details
md_is_link_reference_definition_helper in md4c 0.2.5 has a heap-based buffer over-read because md_is_link_label mishandles loop termination.

## References
- https://github.com/mity/md4c/issues/37
