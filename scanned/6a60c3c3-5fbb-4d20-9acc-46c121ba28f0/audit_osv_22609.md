# [M] CVE-2022-3341

## Summary
Severity: Medium
Advisory: CVE-2022-3341
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-01-12
Source: https://osv.dev/vulnerability/CVE-2022-3341
Type: osv

## Details
A null pointer dereference issue was discovered in 'FFmpeg' in decode_main_header() function of libavformat/nutdec.c file. The flaw occurs because the function lacks check of the return value of avformat_new_stream() and triggers the null pointer dereference error, causing an application to crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3341.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3341
- https://bugzilla.redhat.com/show_bug.cgi?id=2157054
- https://github.com/FFmpeg/FFmpeg/commit/9cf652cef49d74afe3d454f27d49eb1a1394951e
- https://lists.debian.org/debian-lts-announce/2023/06/msg00016.html
