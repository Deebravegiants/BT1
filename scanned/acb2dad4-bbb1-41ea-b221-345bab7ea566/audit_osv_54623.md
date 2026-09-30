# [M] CVE-2024-22653

## Summary
Severity: Medium
Advisory: CVE-2024-22653
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-29
Source: https://osv.dev/vulnerability/CVE-2024-22653
Type: osv

## Details
yasm commit 9defefae was discovered to contain a NULL pointer dereference via the yasm_section_bcs_append function at section.c.

## References
- https://gist.github.com/TimChan2001/03e5792b15d0a34bfaad970e37c17660
- https://github.com/yasm/yasm/issues/247
