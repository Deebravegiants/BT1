# [H] A vulnerability classified as problematic has been found in ffmpeg

## Summary
Severity: High
Advisory: JLSEC-2025-120
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-10-19
Source: https://osv.dev/vulnerability/JLSEC-2025-120
Type: osv

## Affected
- Julia: `FFMPEG_jll` — affected >=4.4.0+0 <4.4.4+0

## Details
A vulnerability classified as problematic has been found in ffmpeg. This affects an unknown part of the file `libavcodec/rpzaenc.c` of the component QuickTime RPZA Video Encoder. The manipulation of the argument `y_size` leads to out-of-bounds read. It is possible to initiate the attack remotely. The name of the patch is 92f9b28ed84a77138105475beba16c146bdaf984. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-213543.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/92f9b28ed84a77138105475beba16c146bdaf984
- https://security.gentoo.org/glsa/202312-14
- https://vuldb.com/?id.213543
