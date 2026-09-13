# [H] CVE-2018-7322

## Summary
Severity: High
Advisory: CVE-2018-7322
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7322
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-dcm.c had an infinite loop that was addressed by checking for integer wraparound.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=afc780e2c796e971bb7d164103f4f0d10d3c25b5
- http://www.securityfocus.com/bid/103158
- https://lists.debian.org/debian-lts-announce/2018/04/msg00018.html
- https://lists.debian.org/debian-lts-announce/2019/01/msg00010.html
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14411
