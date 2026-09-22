# [H] CVE-2017-11411

## Summary
Severity: High
Advisory: CVE-2017-11411
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11411
Type: osv

## Details
In Wireshark through 2.0.13 and 2.2.x through 2.2.7, the openSAFETY dissector could crash or exhaust system memory. This was addressed in epan/dissectors/packet-opensafety.c by adding length validation. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-9350.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a83a324acdfc07a0ca8b65e6ebaba3374ab19c76
- https://www.wireshark.org/security/wnpa-sec-2017-28.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13755
