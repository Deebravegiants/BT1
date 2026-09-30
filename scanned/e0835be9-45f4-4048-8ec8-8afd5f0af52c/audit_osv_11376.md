# [M] CVE-2017-7586

## Summary
Severity: Medium
Advisory: CVE-2017-7586
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-07
Source: https://osv.dev/vulnerability/CVE-2017-7586
Type: osv

## Details
In libsndfile before 1.0.28, an error in the "header_read()" function (common.c) when handling ID3 tags can be exploited to cause a stack-based buffer overflow via a specially crafted FLAC file.

## References
- http://www.securityfocus.com/bid/97522
- http://www.mega-nerd.com/libsndfile/#History
- http://www.mega-nerd.com/libsndfile/NEWS
- https://security.gentoo.org/glsa/201707-04
- https://github.com/erikd/libsndfile/commit/708e996c87c5fae77b104ccfeb8f6db784c32074
- https://github.com/erikd/libsndfile/commit/f457b7b5ecfe91697ed01cfc825772c4d8de1236
