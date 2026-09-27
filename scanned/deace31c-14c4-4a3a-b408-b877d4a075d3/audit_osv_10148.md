# [M] CVE-2017-14058

## Summary
Severity: Medium
Advisory: CVE-2017-14058
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14058
Type: osv

## Details
In FFmpeg 2.4 and 3.3.3, the read_data function in libavformat/hls.c does not restrict reload attempts for an insufficient list, which allows remote attackers to cause a denial of service (infinite loop).

## References
- http://www.securityfocus.com/bid/100629
- https://lists.debian.org/debian-lts-announce/2019/03/msg00041.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/7ba100d3e6e8b1e5d5342feb960a7f081d6e15af
- https://github.com/FFmpeg/FFmpeg/commit/7ec414892ddcad88313848494b6fc5f437c9ca4a
