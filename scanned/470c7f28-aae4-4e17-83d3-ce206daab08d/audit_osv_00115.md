# [H] ALPINE-CVE-2016-4563

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-4563
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-4563
Type: osv

## Affected
- Alpine:v3.2: `imagemagick` — affected >=0 <6.9.6.8-r0
- Alpine:v3.3: `imagemagick` — affected >=0 <6.9.6.8-r0

## Details
The TraceStrokePolygon function in MagickCore/draw.c in ImageMagick before 6.9.4-0 and 7.x before 7.0.1-2 mishandles the relationship between the BezierQuantum value and certain strokes data, which allows remote attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact via a crafted file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-4563
