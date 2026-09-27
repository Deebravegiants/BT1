# [M] JLSEC-2026-131

## Summary
Severity: Medium
Advisory: JLSEC-2026-131
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-131
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.2.4+0

## Details
In ImfChromaticities.cpp routine RGBtoXYZ(), there are some division operations such as `float Z = (1 - chroma.white.x - chroma.white.y) * Y / chroma.white.y;` and `chroma.green.y * (X + Z))) / d;` but the divisor is not checked for a 0 value. A specially crafted file could trigger a divide-by-zero condition which could affect the availability of programs linked with OpenEXR.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2019789
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I2JSMJ7HLWFPYYV7IAQZD5ZUUUN7RWBN/
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299
