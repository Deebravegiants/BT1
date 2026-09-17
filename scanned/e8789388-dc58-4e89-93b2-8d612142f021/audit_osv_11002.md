# [H] CVE-2017-5596

## Summary
Severity: High
Advisory: CVE-2017-5596
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-25
Source: https://osv.dev/vulnerability/CVE-2017-5596
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.3 and 2.0.0 to 2.0.9, the ASTERIX dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-asterix.c by changing a data type to avoid an integer overflow.

## References
- http://www.securitytracker.com/id/1037694
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=781f03580c81339513bb1238b202b72469a1240b
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/95795
- https://www.wireshark.org/security/wnpa-sec-2017-01.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13344
- https://code.wireshark.org/review/#/c/19746/
