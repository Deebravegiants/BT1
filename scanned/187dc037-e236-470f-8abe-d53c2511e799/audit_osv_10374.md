# [H] CVE-2017-15190

## Summary
Severity: High
Advisory: CVE-2017-15190
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-10
Source: https://osv.dev/vulnerability/CVE-2017-15190
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.1, the RTSP dissector could crash. This was addressed in epan/dissectors/packet-rtsp.c by correcting the scope of a variable.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e27870eaa6efa1c2dac08aa41a67fe9f0839e6e0
- http://www.securityfocus.com/bid/101229
- https://www.wireshark.org/security/wnpa-sec-2017-45.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14077
- https://code.wireshark.org/review/23635
