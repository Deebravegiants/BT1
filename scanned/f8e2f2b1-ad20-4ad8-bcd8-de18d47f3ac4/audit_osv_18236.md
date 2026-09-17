# [H] CVE-2020-25464

## Summary
Severity: High
Advisory: CVE-2020-25464
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-04
Source: https://osv.dev/vulnerability/CVE-2020-25464
Type: osv

## Details
Heap buffer overflow at moddable/xs/sources/xsDebug.c in Moddable SDK before before 20200903. The top stack frame is only partially initialized because the stack overflowed while creating the frame. This leads to a crash in the code sending the stack frame to the debugger.

## References
- https://github.com/Moddable-OpenSource/moddable/issues/431
