# [M] CVE-2019-13309

## Summary
Severity: Medium
Advisory: CVE-2019-13309
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-05
Source: https://osv.dev/vulnerability/CVE-2019-13309
Type: osv

## Details
ImageMagick 7.0.8-50 Q16 has memory leaks at AcquireMagickMemory because of mishandling the NoSuchImage error in CLIListOperatorImages in MagickWand/operation.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00069.html
- https://usn.ubuntu.com/4192-1/
- https://www.debian.org/security/2020/dsa-4712
- https://github.com/ImageMagick/ImageMagick/commit/5f21230b657ccd65452dd3d94c5b5401ba691a2d
- https://github.com/ImageMagick/ImageMagick/issues/1616
- https://github.com/ImageMagick/ImageMagick6/commit/5982632109cad48bc6dab867298fdea4dea57c51
