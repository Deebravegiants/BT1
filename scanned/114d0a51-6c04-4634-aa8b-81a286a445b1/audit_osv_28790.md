# [M] CVE-2024-36613

## Summary
Severity: Medium
Advisory: CVE-2024-36613
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-03
Source: https://osv.dev/vulnerability/CVE-2024-36613
Type: osv

## Details
FFmpeg n6.1.1 has a vulnerability in the DXA demuxer of the libavformat library allowing for an integer overflow, potentially resulting in a denial-of-service (DoS) condition or other undefined behavior.

## References
- https://gist.github.com/1047524396/0f4d90ef87553f772f888223085ac806
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/dxa.c#L125
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36613.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36613
- https://github.com/ffmpeg/ffmpeg/commit/50d8e4f27398fd5778485a827d7a2817921f8540
