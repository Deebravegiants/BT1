# [H] CVE-2017-13767

## Summary
Severity: High
Advisory: CVE-2017-13767
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13767
Type: osv

## Details
In Wireshark 2.4.0, 2.2.0 to 2.2.8, and 2.0.0 to 2.0.14, the MSDP dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-msdp.c by adding length validation.

## References
- http://www.securityfocus.com/bid/100549
- http://www.securitytracker.com/id/1039254
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6f18ace2a2683418a9368a8dfd92da6bd8213e15
- https://www.wireshark.org/security/wnpa-sec-2017-38.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13933
