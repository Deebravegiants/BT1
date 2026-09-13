# [C] Expat (aka libexpat) before 2.4.4 has a signed integer overflow in `XML_GetBuffer`, for...

## Summary
Severity: Critical
Advisory: JLSEC-2025-50
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/JLSEC-2025-50
Type: osv

## Affected
- Julia: `Expat_jll` — affected >=0 <2.4.4+0

## Details
Expat (aka libexpat) before 2.4.4 has a signed integer overflow in `XML_GetBuffer`, for configurations with a nonzero `XML_CONTEXT_BYTES`.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://github.com/libexpat/libexpat/pull/550
- https://lists.debian.org/debian-lts-announce/2022/03/msg00007.html
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220217-0001/
- https://www.debian.org/security/2022/dsa-5073
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.tenable.com/security/tns-2022-05
