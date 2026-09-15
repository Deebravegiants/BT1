# [M] CVE-2021-23172

## Summary
Severity: Medium
Advisory: CVE-2021-23172
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-23172
Type: osv

## Details
A vulnerability was found in SoX, where a heap-buffer-overflow occurs in function startread() in hcom.c file. The vulnerability is exploitable with a crafted hcomn file, that could cause an application to crash.

## References
- https://security.archlinux.org/CVE-2021-23172
- https://access.redhat.com/security/cve/CVE-2021-23172
- https://bugzilla.redhat.com/show_bug.cgi?id=1975666
- https://sourceforge.net/p/sox/bugs/350/
