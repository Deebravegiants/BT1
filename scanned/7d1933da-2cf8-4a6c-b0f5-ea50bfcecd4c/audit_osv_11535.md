# [C] CVE-2017-8358

## Summary
Severity: Critical
Advisory: CVE-2017-8358
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-30
Source: https://osv.dev/vulnerability/CVE-2017-8358
Type: osv

## Details
LibreOffice before 2017-03-17 has an out-of-bounds write caused by a heap-based buffer overflow related to the ReadJPEG function in vcl/source/filter/jpeg/jpegc.cxx.

## References
- http://www.securityfocus.com/bid/98395
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=889
- https://github.com/LibreOffice/core/commit/6e6e54f944a5ebb49e9110bdeff844d00a96c56c
