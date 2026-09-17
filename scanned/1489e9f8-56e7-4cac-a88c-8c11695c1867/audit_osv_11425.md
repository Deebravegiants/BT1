# [H] CVE-2017-7704

## Summary
Severity: High
Advisory: CVE-2017-7704
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7704
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5, the DOF dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-dof.c by using a different integer data type and adjusting a return value.

## References
- http://www.securitytracker.com/id/1038262
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6032b0fe5fc1176ab77e03e20765f95fbd21b19e
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=da53a90b6895e47e03c5de05edf84bd99d535fd8
- http://www.securityfocus.com/bid/97634
- https://security.gentoo.org/glsa/201706-12
- https://www.wireshark.org/security/wnpa-sec-2017-17.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13453
