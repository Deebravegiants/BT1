# [M] CVE-2019-18853

## Summary
Severity: Medium
Advisory: CVE-2019-18853
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-11
Source: https://osv.dev/vulnerability/CVE-2019-18853
Type: osv

## Details
ImageMagick before 7.0.9-0 allows remote attackers to cause a denial of service because XML_PARSE_HUGE is not properly restricted in coders/svg.c, related to SVG and libxml2.

## References
- https://fortiguard.com/zeroday/FG-VD-19-136
- https://github.com/ImageMagick/ImageMagick/commit/ec9c8944af2bfc65c697ca44f93a727a99b405f1
