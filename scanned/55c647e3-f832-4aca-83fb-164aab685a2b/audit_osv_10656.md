# [H] CVE-2017-18009

## Summary
Severity: High
Advisory: CVE-2017-18009
Aliases: GHSA-83rh-hx5x-q9p5, PYSEC-2026-2810, PYSEC-2026-702
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-01
Source: https://osv.dev/vulnerability/CVE-2017-18009
Type: osv

## Details
In OpenCV 3.3.1, a heap-based buffer over-read exists in the function cv::HdrDecoder::checkSignature in modules/imgcodecs/src/grfmt_hdr.cpp.

## References
- http://www.securityfocus.com/bid/106945
- https://github.com/opencv/opencv/issues/10479
