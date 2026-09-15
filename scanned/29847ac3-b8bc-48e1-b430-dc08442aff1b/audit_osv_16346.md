# [M] CVE-2019-5718

## Summary
Severity: Medium
Advisory: CVE-2019-5718
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-08
Source: https://osv.dev/vulnerability/CVE-2019-5718
Type: osv

## Details
In Wireshark 2.6.0 to 2.6.5 and 2.4.0 to 2.4.11, the RTSE dissector and other ASN.1 dissectors could crash. This was addressed in epan/charsets.c by adding a get_t61_string length check.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=cd09cb5cfb673beca3cce20b1d6a9bc67a134ae1
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://www.securityfocus.com/bid/106482
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-03.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15373
