# [M] CVE-2016-9374

## Summary
Severity: Medium
Advisory: CVE-2016-9374
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-17
Source: https://osv.dev/vulnerability/CVE-2016-9374
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.1 and 2.0.0 to 2.0.7, the AllJoyn dissector could crash with a buffer over-read, triggered by network traffic or a capture file. This was addressed in epan/dissectors/packet-alljoyn.c by ensuring that a length variable properly tracked the state of a signature variable.

## References
- http://www.securitytracker.com/id/1037313
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a5770b6559b6e6765c4ef800e85ae42781ea4900
- http://www.debian.org/security/2016/dsa-3719
- http://www.securityfocus.com/bid/94369
- https://www.wireshark.org/security/wnpa-sec-2016-59.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12953
