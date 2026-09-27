# [M] CVE-2017-8313

## Summary
Severity: Medium
Advisory: CVE-2017-8313
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-8313
Type: osv

## Details
Heap out-of-bound read in ParseJSS in VideoLAN VLC before 2.2.5 due to missing check of string termination allows attackers to read data beyond allocated memory and potentially crash the process via a crafted subtitles file.

## References
- http://git.videolan.org/?p=vlc/vlc-2.2.git%3Ba=commitdiff%3Bh=05b653355ce303ada3b5e0e645ae717fea39186c
- http://www.securityfocus.com/bid/98633
- http://www.debian.org/security/2017/dsa-3899
- https://security.gentoo.org/glsa/201707-10
