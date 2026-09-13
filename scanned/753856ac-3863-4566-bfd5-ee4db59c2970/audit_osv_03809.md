# [H] ALPINE-CVE-2026-52859

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-52859
Ecosystem: Alpine:v3.23
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-52859
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0567-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0565, the update_snapshot() function in src/terminal.c copies the visible terminal screen into the scrollback buffer when a snapshot is taken. For each screen cell it walks the cell's chars[] array with no upper bound, stopping only when it encounters a NUL terminator. When a cell legitimately fills all VTERM_MAX_CHARS_PER_CELL (6) slots — a base character plus five combining marks — the bundled libvterm returns the array without a terminating NUL, so the loop reads past the fixed six-element array and appends the out-of-bounds values to a buffer reserved for only six characters. A program whose output is rendered inside a :terminal window can trigger this with a short byte sequence and no Vim scripting, leading to a crash. This issue has been patched in version 9.2.0565.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-52859
