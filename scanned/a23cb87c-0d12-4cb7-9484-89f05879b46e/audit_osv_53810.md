# [H] CVE-2023-26314

## Summary
Severity: High
Advisory: CVE-2023-26314
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-02-22
Source: https://osv.dev/vulnerability/CVE-2023-26314
Type: osv

## Details
The mono package before 6.8.0.105+dfsg-3.3 for Debian allows arbitrary code execution because the application/x-ms-dos-executable MIME type is associated with an un-sandboxed Mono CLR interpreter.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00037.html
- https://www.openwall.com/lists/oss-security/2023/01/05/1
- https://bugs.debian.org/972146
