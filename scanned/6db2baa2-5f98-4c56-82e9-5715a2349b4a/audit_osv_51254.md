# [M] CVE-2021-23210

## Summary
Severity: Medium
Advisory: CVE-2021-23210
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-23210
Type: osv

## Details
A floating point exception (divide-by-zero) issue was discovered in SoX in functon read_samples() of voc.c file. An attacker with a crafted file, could cause an application to crash.

## References
- https://access.redhat.com/security/cve/CVE-2021-23210
- https://security.archlinux.org/CVE-2021-23210
- https://bugzilla.redhat.com/show_bug.cgi?id=1975670
- https://sourceforge.net/p/sox/bugs/351/
