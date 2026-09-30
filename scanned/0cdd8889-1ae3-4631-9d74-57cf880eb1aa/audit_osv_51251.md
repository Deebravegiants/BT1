# [M] CVE-2021-23159

## Summary
Severity: Medium
Advisory: CVE-2021-23159
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-23159
Type: osv

## Details
A vulnerability was found in SoX, where a heap-buffer-overflow occurs in function lsx_read_w_buf() in formats_i.c file. The vulnerability is exploitable with a crafted file, that could cause an application to crash.

## References
- https://access.redhat.com/security/cve/CVE-2021-23159
- https://security.archlinux.org/CVE-2021-23159
- https://bugzilla.redhat.com/show_bug.cgi?id=1975671
- https://sourceforge.net/p/sox/bugs/352/
