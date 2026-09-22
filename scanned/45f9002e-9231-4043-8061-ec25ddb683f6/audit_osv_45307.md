# [M] In Expat (aka libexpat) before 2.4.5, an attacker can trigger stack exhaustion in `build_model` via...

## Summary
Severity: Medium
Advisory: JLSEC-2025-54
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-54
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.4.8+0

## Details
In Expat (aka libexpat) before 2.4.5, an attacker can trigger stack exhaustion in `build_model` via a large nesting depth in the DTD element.

## References
- http://www.openwall.com/lists/oss-security/2022/02/19/1
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://github.com/libexpat/libexpat/pull/558
- https://lists.debian.org/debian-lts-announce/2022/03/msg00007.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3UFRBA3UQVIQKXTBUQXDWQOVWNBKLERU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y27XO3JMKAOMQZVPS3B4MJGEAHCZF5OM/
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220303-0008/
- https://www.debian.org/security/2022/dsa-5085
- https://www.oracle.com/security-alerts/cpuapr2022.html
