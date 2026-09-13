# [H] CVE-2017-6470

## Summary
Severity: High
Advisory: CVE-2017-6470
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6470
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is an IAX2 infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-iax2.c by constraining packet lateness.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=0b89174ef4c531a1917437fff586fe525ee7bf2d
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96563
- https://www.wireshark.org/security/wnpa-sec-2017-10.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13432
