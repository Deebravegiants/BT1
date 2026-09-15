# [M] CVE-2020-27545

## Summary
Severity: Medium
Advisory: CVE-2020-27545
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2020-27545
Type: osv

## Details
libdwarf before 20201017 has a one-byte out-of-bounds read because of an invalid pointer dereference via an invalid line table in a crafted object.

## References
- http://web.archive.org/web/20190601140703/https://sourceforge.net/projects/libdwarf/
- https://sourceforge.net/projects/libdwarf/
- https://www.prevanders.net/dwarfbug.html#DW202010-001
- https://bugzilla.redhat.com/show_bug.cgi?id=2025694
- https://github.com/davea42/libdwarf-code/commit/95f634808c01f1c61bbec56ed2395af997f397ea
