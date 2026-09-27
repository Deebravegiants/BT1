# [H] CVE-2017-16803

## Summary
Severity: High
Advisory: CVE-2017-16803
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-16803
Type: osv

## Details
In Libav through 11.11 and 12.x through 12.1, the smacker_decode_tree function in libavcodec/smacker.c does not properly restrict tree recursion, which allows remote attackers to cause a denial of service (bitstream.c:build_table() out-of-bounds read and application crash) via a crafted Smacker stream.

## References
- http://www.securityfocus.com/bid/101882
- https://security.gentoo.org/glsa/201811-19
- https://www.debian.org/security/2018/dsa-4119
- https://bugzilla.libav.org/show_bug.cgi?id=1098
- https://github.com/libav/libav/commit/cd4663dc80323ba64989d0c103d51ad3ee0e9c2f
