# [M] CVE-2021-33844

## Summary
Severity: Medium
Advisory: CVE-2021-33844
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-33844
Type: osv

## Details
A floating point exception (divide-by-zero) issue was discovered in SoX in functon startread() of wav.c file. An attacker with a crafted wav file, could cause an application to crash.

## References
- https://security.archlinux.org/CVE-2021-33844
- https://access.redhat.com/security/cve/CVE-2021-33844
- https://bugzilla.redhat.com/show_bug.cgi?id=1975664
- https://sourceforge.net/p/sox/bugs/349/
