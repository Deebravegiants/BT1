# [H] CVE-2017-11410

## Summary
Severity: High
Advisory: CVE-2017-11410
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-18
Source: https://osv.dev/vulnerability/CVE-2017-11410
Type: osv

## Details
In Wireshark through 2.0.13 and 2.2.x through 2.2.7, the WBXML dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-wbxml.c by adding validation of the relationships between indexes and lengths. NOTE: this vulnerability exists because of an incomplete fix for CVE-2017-7702.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=3c7168cc5f044b4da8747d35da0b2b204dabf398
- https://www.wireshark.org/security/wnpa-sec-2017-13.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13796
