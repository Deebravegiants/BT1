# [H] CVE-2017-6473

## Summary
Severity: High
Advisory: CVE-2017-6473
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6473
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is a K12 file parser crash, triggered by a malformed capture file. This was addressed in wiretap/k12.c by validating the relationships between lengths and offsets.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=7edc761a01cda8e1b37677f673985582330317d2
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96565
- https://www.wireshark.org/security/wnpa-sec-2017-09.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13431
