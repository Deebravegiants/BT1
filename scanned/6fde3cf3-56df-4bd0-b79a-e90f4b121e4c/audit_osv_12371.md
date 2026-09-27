# [C] CVE-2018-11545

## Summary
Severity: Critical
Advisory: CVE-2018-11545
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-29
Source: https://osv.dev/vulnerability/CVE-2018-11545
Type: osv

## Details
md4c 0.2.5 has a heap-based buffer overflow in md_merge_lines because md_is_link_label mishandles the case of a link label composed solely of backslash escapes.

## References
- https://github.com/mity/md4c/issues/39
