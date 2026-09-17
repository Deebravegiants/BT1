# [H] CVE-2026-5525

## Summary
Severity: High
Advisory: CVE-2026-5525
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-5525
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in Notepad++ version 8.9.3 in the file drop handler component. When a user drags and drops a directory path of exactly 259 characters without a trailing backslash, the application appends a backslash and null terminator without proper bounds checking, resulting in a stack buffer overflow and application crash (STATUS_STACK_BUFFER_OVERRUN).

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/issues/17921
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/bfe7514d68bc559534c046c4ef2d1865267aa2b0
- https://github.com/notepad-plus-plus/notepad-plus-plus/pull/17930
