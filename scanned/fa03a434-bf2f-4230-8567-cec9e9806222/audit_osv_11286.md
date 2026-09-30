# [H] CVE-2017-7223

## Summary
Severity: High
Advisory: CVE-2017-7223
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-22
Source: https://osv.dev/vulnerability/CVE-2017-7223
Type: osv

## Details
GNU assembler in GNU Binutils 2.28 is vulnerable to a global buffer overflow (of size 1) while attempting to unget an EOF character from the input stream, potentially leading to a program crash.

## References
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=20898
