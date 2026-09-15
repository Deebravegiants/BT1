# [H] CVE-2017-6469

## Summary
Severity: High
Advisory: CVE-2017-6469
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-04
Source: https://osv.dev/vulnerability/CVE-2017-6469
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.4 and 2.0.0 to 2.0.10, there is an LDSS dissector crash, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-ldss.c by ensuring that memory is allocated for a certain data structure.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4f753c127082d5e28abf482d6d175cbfee6661f7
- http://www.debian.org/security/2017/dsa-3811
- http://www.securityfocus.com/bid/96577
- https://www.wireshark.org/security/wnpa-sec-2017-03.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13346
