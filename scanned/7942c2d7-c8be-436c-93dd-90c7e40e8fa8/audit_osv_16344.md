# [M] CVE-2019-5716

## Summary
Severity: Medium
Advisory: CVE-2019-5716
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5716
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.5, the 6LoWPAN dissector could crash. This was addressed in epan/dissectors/packet-6lowpan.c by avoiding use of a TVB before its creation.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2b2eea1793dbff813896e1ae9dff1bedb39ee010
- http://www.securityfocus.com/bid/106482
- https://lists.debian.org/debian-lts-announce/2019/01/msg00022.html
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-01.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15217
