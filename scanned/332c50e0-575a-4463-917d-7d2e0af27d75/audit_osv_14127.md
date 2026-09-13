# [H] CVE-2018-7329

## Summary
Severity: High
Advisory: CVE-2018-7329
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7329
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-s7comm.c had an infinite loop that was addressed by correcting off-by-one errors.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=d8a0cbc4f2979e0b1cadbe79f0b8b4ecb92477be
- http://www.securityfocus.com/bid/103158
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14423
