# [H] A vulnerability, which was classified as critical, was found in FFmpeg up to 5.1.5

## Summary
Severity: High
Advisory: JLSEC-2025-134
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-134
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.1+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A vulnerability, which was classified as critical, was found in FFmpeg up to 5.1.5. This affects the function `fill_audiodata` of the file `/libswresample/swresample.c`. The manipulation leads to heap-based buffer overflow. It is possible to initiate the attack remotely. This issue was fixed in version 6.0 by 9903ba28c28ab18dc7b7b6fb8571cc8b5caae1a6 but a backport for 5.1 was forgotten. The exploit has been disclosed to the public and may be used. Upgrading to version 5.1.6 and 6.0 9903ba28c28ab18dc7b7b6fb8571cc8b5caae1a6 is able to address this issue. It is recommended to upgrade the affected component.

## References
- https://ffmpeg.org/
- https://github.com/CookedMelon/ReportCVE/tree/main/FFmpeg/poc5
- https://github.com/CookedMelon/ReportCVE/tree/main/FFmpeg/poc6
- https://vuldb.com/?ctiid.273945
- https://vuldb.com/?id.273945
