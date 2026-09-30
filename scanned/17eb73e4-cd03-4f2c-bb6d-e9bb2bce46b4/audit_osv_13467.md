# [M] CVE-2018-1999014

## Summary
Severity: Medium
Advisory: CVE-2018-1999014
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999014
Type: osv

## Details
FFmpeg before commit bab0716c7f4793ec42e05a5aa7e80d82a0dd4e75 contains an out of array access vulnerability in MXF format demuxer that can result in DoS. This attack appear to be exploitable via specially crafted MXF file which has to be provided as input. This vulnerability appears to have been fixed in bab0716c7f4793ec42e05a5aa7e80d82a0dd4e75 and later.

## References
- http://www.securityfocus.com/bid/104896
- https://github.com/FFmpeg/FFmpeg/commit/bab0716c7f4793ec42e05a5aa7e80d82a0dd4e75
