# [M] CVE-2024-36615

## Summary
Severity: Medium
Advisory: CVE-2024-36615
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36615
Type: osv

## Details
FFmpeg n7.0 has a race condition vulnerability in the VP9 decoder. This could lead to a data race if video encoding parameters were being exported, as the side data would be attached in the decoder thread while being read in the output thread.

## References
- https://gist.github.com/1047524396/c44e5eaafa8f408eea0c9411205990fb
- https://github.com/FFmpeg/FFmpeg/blob/n7.0/libavcodec/vp9.c#L1738
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36615.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36615
- https://github.com/ffmpeg/ffmpeg/commit/0ba058579f332b3060d8470a04ddd3fbf305be61
