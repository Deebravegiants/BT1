# [H] CVE-2016-4563

## Summary
Severity: High
Advisory: CVE-2016-4563
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-04
Source: https://osv.dev/vulnerability/CVE-2016-4563
Type: osv

## Details
The TraceStrokePolygon function in MagickCore/draw.c in ImageMagick before 6.9.4-0 and 7.x before 7.0.1-2 mishandles the relationship between the BezierQuantum value and certain strokes data, which allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.imagemagick.org/script/changelog.php
- https://github.com/ImageMagick/ImageMagick/commit/726812fa2fa7ce16bcf58f6e115f65427a1c0950
