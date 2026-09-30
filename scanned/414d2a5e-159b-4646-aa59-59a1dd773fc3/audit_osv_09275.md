# [M] CVE-2016-9372

## Summary
Severity: Medium
Advisory: CVE-2016-9372
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-17
Source: https://osv.dev/vulnerability/CVE-2016-9372
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.1, the Profinet I/O dissector could loop excessively, triggered by network traffic or a capture file. This was addressed in plugins/profinet/packet-pn-rtc-one.c by rejecting input with too many I/O objects.

## References
- http://www.securitytracker.com/id/1037313
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4127e3930ef663114567002001f44e01eba8a250
- http://www.securityfocus.com/bid/94368
- https://www.wireshark.org/security/wnpa-sec-2016-58.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12851
