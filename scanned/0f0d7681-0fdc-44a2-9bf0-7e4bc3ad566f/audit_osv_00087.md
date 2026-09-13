# [H] ALPINE-CVE-2016-2328

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2328
Ecosystem: Alpine:v3.3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2328
Type: osv

## Affected
- Alpine:v3.3: `ffmpeg` — affected >=0 <2.8.11-r0

## Details
libswscale/swscale_unscaled.c in FFmpeg before 2.8.6 does not validate certain height values, which allows remote attackers to cause a denial of service (out-of-bounds array read access) or possibly have unspecified other impact via a crafted .cine file, related to the bayer_to_rgb24_wrapper and bayer_to_yv12_wrapper functions.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2328
