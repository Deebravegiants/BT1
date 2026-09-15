# [M] CVE-2025-27465

## Summary
Severity: Medium
Advisory: CVE-2025-27465
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-07-16
Source: https://osv.dev/vulnerability/CVE-2025-27465
Type: osv

## Details
Certain instructions need intercepting and emulating by Xen.  In some
cases Xen emulates the instruction by replaying it, using an executable
stub.  Some instructions may raise an exception, which is supposed to be
handled gracefully.  Certain replayed instructions have additional logic
to set up and recover the changes to the arithmetic flags.

For replayed instructions where the flags recovery logic is used, the
metadata for exception handling was incorrect, preventing Xen from
handling the the exception gracefully, treating it as fatal instead.

## References
- http://www.openwall.com/lists/oss-security/2025/07/01/1
- https://xenbits.xenproject.org/xsa/advisory-470.html
- http://xenbits.xen.org/xsa/advisory-470.html
