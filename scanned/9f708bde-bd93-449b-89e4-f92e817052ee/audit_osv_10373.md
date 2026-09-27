# [H] CVE-2017-15189

## Summary
Severity: High
Advisory: CVE-2017-15189
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15189
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.1, the DOCSIS dissector could go into an infinite loop. This was addressed in plugins/docsis/packet-docsis.c by adding decrements.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=625bab309d9dd21db2d8ae2aa3511810d32842a8
- http://www.securityfocus.com/bid/101228
- https://www.wireshark.org/security/wnpa-sec-2017-46.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14080
- https://code.wireshark.org/review/23663
