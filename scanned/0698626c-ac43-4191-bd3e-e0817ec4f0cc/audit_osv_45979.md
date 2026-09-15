# [M] JLSEC-2026-538

## Summary
Severity: Medium
Advisory: JLSEC-2026-538
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/JLSEC-2026-538
Type: osv

## Affected
- Julia: `OpenJpeg_jll` — affected >=0 <2.4.0+0

## Details
There's a flaw in openjpeg in versions prior to 2.4.0 in `src/lib/openjp2/pi.c`. When an attacker is able to provide crafted input to be processed by the openjpeg encoder, this could cause an out-of-bounds read. The greatest impact from this flaw is to application availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1907510
- https://lists.debian.org/debian-lts-announce/2021/02/msg00011.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WJUPGIZE6A4O52EBOF75MCXJOL6MUCRV/
- https://security.gentoo.org/glsa/202101-29
- https://www.debian.org/security/2021/dsa-4882
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
