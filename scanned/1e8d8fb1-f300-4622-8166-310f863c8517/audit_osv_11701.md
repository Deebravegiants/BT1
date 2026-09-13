# [H] CVE-2017-9350

## Summary
Severity: High
Advisory: CVE-2017-9350
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9350
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the openSAFETY dissector could crash or exhaust system memory. This was addressed in epan/dissectors/packet-opensafety.c by checking for a negative length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=dbc7cb0bbdd501fa96e0cb98668f6d6bf17ac4e6
- http://www.securityfocus.com/bid/98806
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-28.html
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=1212
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13649
