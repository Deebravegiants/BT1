# [H] CVE-2017-13764

## Summary
Severity: High
Advisory: CVE-2017-13764
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-30
Source: https://osv.dev/vulnerability/CVE-2017-13764
Type: osv

## Details
In Wireshark 2.4.0, the Modbus dissector could crash with a NULL pointer dereference. This was addressed in epan/dissectors/packet-mbtcp.c by adding length validation.

## References
- http://www.securityfocus.com/bid/100545
- http://www.securitytracker.com/id/1039254
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=b87ffbd12bddf64582c0a6e082b462744474de94
- https://www.wireshark.org/security/wnpa-sec-2017-40.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13925
