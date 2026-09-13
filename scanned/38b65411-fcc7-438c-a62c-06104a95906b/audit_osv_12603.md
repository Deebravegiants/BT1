# [H] CVE-2018-13300

## Summary
Severity: High
Advisory: CVE-2018-13300
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-07-05
Source: https://osv.dev/vulnerability/CVE-2018-13300
Type: osv

## Details
In FFmpeg 3.2 and 4.0.1, an improper argument (AVCodecParameters) passed to the avpriv_request_sample function in the handle_eac3 function in libavformat/movenc.c may trigger an out-of-array read while converting a crafted AVI file to MPEG4, leading to a denial of service and possibly an information disclosure.

## References
- http://www.securityfocus.com/bid/104675
- https://www.debian.org/security/2018/dsa-4249
- https://github.com/FFmpeg/FFmpeg/commit/95556e27e2c1d56d9e18f5db34d6f756f3011148
- https://github.com/FFmpeg/FFmpeg/commit/e6d3fd942f772f54ab6a5ca619cdaadef26b7702
