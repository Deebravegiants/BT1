# [M] CVE-2017-7700

## Summary
Severity: Medium
Advisory: CVE-2017-7700
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7700
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the NetScaler file parser could go into an infinite loop, triggered by a malformed capture file. This was addressed in wiretap/netscaler.c by ensuring a nonzero record size.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8fc0af859de4993951a915ad735be350221f3f53
- http://www.securityfocus.com/bid/97631
- http://www.securitytracker.com/id/1038262
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://security.gentoo.org/glsa/201706-12
- https://www.wireshark.org/security/wnpa-sec-2017-14.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13478
