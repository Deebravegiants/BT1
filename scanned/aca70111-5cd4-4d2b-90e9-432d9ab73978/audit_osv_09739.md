# [H] CVE-2017-11188

## Summary
Severity: High
Advisory: CVE-2017-11188
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-11188
Type: osv

## Details
The ReadDPXImage function in coders\dpx.c in ImageMagick 7.0.6-0 has a large loop vulnerability that can cause CPU exhaustion via a crafted DPX file, related to lack of an EOF check.

## References
- http://www.securityfocus.com/bid/99566
- https://github.com/ImageMagick/ImageMagick/issues/509
