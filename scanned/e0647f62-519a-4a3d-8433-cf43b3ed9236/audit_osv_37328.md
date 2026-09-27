# [H] CVE-2026-30998

## Summary
Severity: High
Advisory: CVE-2026-30998
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-30998
Type: osv

## Details
An improper resource deallocation and closure vulnerability in the tools/zmqsend.c component of FFmpeg v8.0.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted input file.

## References
- https://excellent-oatmeal-319.notion.site/CVE-2026-30998-Resource-Leak-3265a71f9cca4dc58df4632ce8b60a50
- https://ffmpeg.org/doxygen/7.0/zmqsend_8c_source.html
- https://github.com/FFmpeg/FFmpeg/blob/master/tools/zmqsend.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30998.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30998
