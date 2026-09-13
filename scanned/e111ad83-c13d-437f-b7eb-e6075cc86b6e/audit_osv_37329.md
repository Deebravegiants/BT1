# [H] CVE-2026-30999

## Summary
Severity: High
Advisory: CVE-2026-30999
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-30999
Type: osv

## Details
A heap buffer overflow in the av_bprint_finalize() function of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via a crafted input.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30999-Memory-Leak-e0d88ac53e2e42c1b5ef9aa3497e27b6
- https://ffmpeg.org/doxygen/7.0/zmqsend_8c_source.html
- https://github.com/FFmpeg/FFmpeg/blob/master/tools/zmqsend.c
- https://www.ffmpeg.org/download.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30999.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30999
