# [H] CVE-2020-14212

## Summary
Severity: High
Advisory: CVE-2020-14212
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-16
Source: https://osv.dev/vulnerability/CVE-2020-14212
Type: osv

## Details
FFmpeg through 4.3 has a heap-based buffer overflow in avio_get_str in libavformat/aviobuf.c because dnn_backend_native.c calls ff_dnn_load_model_native and a certain index check is omitted.

## References
- https://patchwork.ffmpeg.org/project/ffmpeg/list/?series=1463
- https://security.gentoo.org/glsa/202007-58
- https://trac.ffmpeg.org/ticket/8716
