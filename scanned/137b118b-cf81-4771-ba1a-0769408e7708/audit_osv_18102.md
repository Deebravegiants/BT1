# [H] CVE-2020-24020

## Summary
Severity: High
Advisory: CVE-2020-24020
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-24020
Type: osv

## Details
Buffer Overflow vulnerability in FFMpeg 4.2.3 in dnn_execute_layer_pad in libavfilter/dnn/dnn_backend_native_layer_pad.c due to a call to memcpy without length checks, which could let a remote malicious user execute arbitrary code.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=584f396132aa19d21bb1e38ad9a5d428869290cb
- https://trac.ffmpeg.org/ticket/8718
