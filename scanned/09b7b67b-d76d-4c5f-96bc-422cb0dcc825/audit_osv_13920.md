# [M] CVE-2018-5335

## Summary
Severity: Medium
Advisory: CVE-2018-5335
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/CVE-2018-5335
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.3 and 2.2.0 to 2.2.11, the WCP dissector could crash. This was addressed in epan/dissectors/packet-wcp.c by validating the available buffer length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=086b87376b988c555484349aa115d6e08ac6db07
- http://www.securityfocus.com/bid/102500
- https://lists.debian.org/debian-lts-announce/2018/01/msg00032.html
- https://www.debian.org/security/2018/dsa-4101
- https://www.wireshark.org/security/wnpa-sec-2018-04.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14251
