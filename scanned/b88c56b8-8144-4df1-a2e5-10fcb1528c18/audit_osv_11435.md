# [H] CVE-2017-7748

## Summary
Severity: High
Advisory: CVE-2017-7748
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7748
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the WSP dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-wsp.c by adding a length check.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f55cbcde2c8f74b652add4450b0592082eb6acff
- http://www.securityfocus.com/bid/97628
- https://www.wireshark.org/security/wnpa-sec-2017-21.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13581
