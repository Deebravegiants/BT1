# [M] CVE-2021-3941

## Summary
Severity: Medium
Advisory: CVE-2021-3941
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-3941
Type: osv

## Details
In ImfChromaticities.cpp routine RGBtoXYZ(), there are some division operations such as `float Z = (1 - chroma.white.x - chroma.white.y) * Y / chroma.white.y;` and `chroma.green.y * (X + Z))) / d;` but the divisor is not checked for a 0 value. A specially crafted file could trigger a divide-by-zero condition which could affect the availability of programs linked with OpenEXR.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I2JSMJ7HLWFPYYV7IAQZD5ZUUUN7RWBN/
- https://lists.debian.org/debian-lts-announce/2022/12/msg00022.html
- https://security.gentoo.org/glsa/202210-31
- https://www.debian.org/security/2022/dsa-5299
- https://bugzilla.redhat.com/show_bug.cgi?id=2019789
