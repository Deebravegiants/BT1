# [M] JLSEC-2026-442

## Summary
Severity: Medium
Advisory: JLSEC-2026-442
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/JLSEC-2026-442
Type: osv

## Affected
- Julia: `Ncurses_jll` — affected >=0 <6.2.0+0

## Details
In ncurses 6.1, there is a NULL pointer dereference at function `_nc_parse_entry` in `parse_entry.c` that will lead to a denial of service attack. The product proceeds to the dereference code path even after a "dubious character `*` in name or alias field" detection.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1643754
