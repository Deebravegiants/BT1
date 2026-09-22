# [M] CVE-2024-36618

## Summary
Severity: Medium
Advisory: CVE-2024-36618
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-29
Source: https://osv.dev/vulnerability/CVE-2024-36618
Type: osv

## Details
FFmpeg n6.1.1 has a vulnerability in the AVI demuxer of the libavformat library which allows for an integer overflow, potentially resulting in a denial-of-service (DoS) condition.

## References
- https://gist.github.com/1047524396/a148f3679415a6da53ca112eb2ba1523
- https://github.com/FFmpeg/FFmpeg/blob/n6.1.1/libavformat/avidec.c#L1699
- https://lists.debian.org/debian-lts-announce/2025/02/msg00000.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36618.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36618
- https://github.com/ffmpeg/ffmpeg/commit/7a089ed8e049e3bfcb22de1250b86f2106060857
