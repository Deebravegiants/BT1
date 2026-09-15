# [M] CVE-2017-6829

## Summary
Severity: Medium
Advisory: CVE-2017-6829
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6829
Type: osv

## Details
The decodeSample function in IMA.cpp in Audio File Library (aka audiofile) 0.3.6 allows remote attackers to cause a denial of service (crash) via a crafted file.

## References
- http://www.securityfocus.com/bid/97189
- http://www.debian.org/security/2017/dsa-3814
- http://www.openwall.com/lists/oss-security/2017/03/13/1
- https://blogs.gentoo.org/ago/2017/02/20/audiofile-global-buffer-overflow-in-decodesample-ima-cpp/
- https://github.com/antlarr/audiofile/commit/25eb00ce913452c2e614548d7df93070bf0d066f
- https://github.com/mpruett/audiofile/issues/33
