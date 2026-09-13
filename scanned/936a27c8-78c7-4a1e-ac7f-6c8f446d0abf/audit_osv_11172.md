# [H] CVE-2017-6471

## Summary
Severity: High
Advisory: CVE-2017-6471
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6471
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is a WSP infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-wsp.c by validating the capability length.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=62afef41277dfac37f515207ca73d33306e3302b
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96564
- https://www.wireshark.org/security/wnpa-sec-2017-05.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13348
