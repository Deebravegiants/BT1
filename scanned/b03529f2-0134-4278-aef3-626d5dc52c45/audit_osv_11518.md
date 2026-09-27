# [H] CVE-2017-8326

## Summary
Severity: High
Advisory: CVE-2017-8326
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-29
Source: https://osv.dev/vulnerability/CVE-2017-8326
Type: osv

## Details
libimageworsener.a in ImageWorsener before 1.3.1 has "left shift cannot be represented in type int" undefined behavior issues, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image, related to imagew-bmp.c and imagew-util.c.

## References
- https://security.gentoo.org/glsa/201706-06
- https://blogs.gentoo.org/ago/2017/04/27/imageworsener-two-left-shift/
- https://github.com/jsummers/imageworsener/commit/a00183107d4b84bc8a714290e824ca9c68dac738
