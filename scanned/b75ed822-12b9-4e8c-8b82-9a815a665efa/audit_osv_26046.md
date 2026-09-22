# [H] CVE-2023-50010

## Summary
Severity: High
Advisory: CVE-2023-50010
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2023-50010
Type: osv

## Details
FFmpeg v.n6.1-3-g466799d4f5 allows a buffer over-read at ff_gradfun_blur_line_movdqa_sse2, as demonstrated by a call to the set_encoder_id function in /fftools/ffmpeg_enc.c component.

## References
- https://ffmpeg.org/
- https://git.ffmpeg.org/gitweb/ffmpeg.git/blobdiff/ab0fdaedd1e7224f7e84ea22fcbfaa4ca75a6c06..e4d2666bdc3dbd177a81bbf428654a5f2fa3787a:/libavfilter/vf_gradfun.c
- https://trac.ffmpeg.org/ticket/10702
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50010.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6G7EYH2JAK5OJPVNC6AXYQ5K7YGYNCDN/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IPETICRXUOGRIM4U3BCRTIKE3IZWCSBT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LE3ASLH6QF2E5OVJI5VA3JSEPJFFFMNY/
- https://nvd.nist.gov/vuln/detail/CVE-2023-50010
- https://github.com/FFmpeg/FFmpeg/commit/e4d2666bdc3dbd177a81bbf428654a5f2fa3787a
- https://github.com/FFmpeg/FFmpeg/commit/e809c23786fe297797198a7b9f5d3392d581daf1
