# [H] A vulnerability was found in FFmpeg up to 7.0.1

## Summary
Severity: High
Advisory: JLSEC-2025-133
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-133
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=0 <6.1.2+0
- Julia: `FFplay_jll` — affected >=0 <7.1.0+0

## Details
A vulnerability was found in FFmpeg up to 7.0.1. It has been classified as critical. This affects the function `pnm_decode_frame` in the library `/libavcodec/pnmdec.c`. The manipulation leads to heap-based buffer overflow. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 7.0.2 is able to address this issue. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-273651.

## References
- https://ffmpeg.org/
- https://ffmpeg.org/download.html
- https://github.com/CookedMelon/ReportCVE/tree/main/FFmpeg/poc3
- https://lists.debian.org/debian-lts-announce/2024/10/msg00019.html
- https://vuldb.com/?ctiid.273651
- https://vuldb.com/?id.273651
- https://vuldb.com/?submit.376532
