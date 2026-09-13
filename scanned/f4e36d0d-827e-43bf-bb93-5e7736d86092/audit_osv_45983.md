# [H] JLSEC-2026-541

## Summary
Severity: High
Advisory: JLSEC-2026-541
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-541
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
A flaw was found in openjpeg's `src/lib/openjp2/t2.c` in versions prior to 2.4.0. This flaw allows an attacker to provide crafted input to openjpeg during conversion and encoding, causing an out-of-bounds write. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1907521
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://security.gentoo.org/glsa/202101-29
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
