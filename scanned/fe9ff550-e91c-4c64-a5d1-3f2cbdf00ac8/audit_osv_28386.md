# [H] CVE-2024-32230

## Summary
Severity: High
Advisory: CVE-2024-32230
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/CVE-2024-32230
Type: osv

## Details
FFmpeg 7.0 is vulnerable to Buffer Overflow. There is a negative-size-param bug at libavcodec/mpegvideo_enc.c:1216:21 in load_input_picture in FFmpeg7.0

## References
- https://trac.ffmpeg.org/ticket/10952
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32230.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-32230
