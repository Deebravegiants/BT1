# [M] CVE-2017-9203

## Summary
Severity: Medium
Advisory: CVE-2017-9203
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-9203
Type: osv

## Details
imagew-main.c:960:12 in libimageworsener.a in ImageWorsener 1.3.1 allows remote attackers to cause a denial of service (buffer underflow) via a crafted image, related to imagew-bmp.c.

## References
- https://blogs.gentoo.org/ago/2017/05/20/imageworsener-multiple-vulnerabilities/
- https://github.com/jsummers/imageworsener/commit/a4f247707f08e322f0b41e82c3e06e224240a654
