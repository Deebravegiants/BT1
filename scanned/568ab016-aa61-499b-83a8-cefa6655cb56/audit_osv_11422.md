# [H] CVE-2017-7701

## Summary
Severity: High
Advisory: CVE-2017-7701
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7701
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the BGP dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-bgp.c by using a different integer data type.

## References
- http://www.securitytracker.com/id/1038262
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=fa31f69b407436d0946f84baa0acdcc50962bf7a
- http://www.securityfocus.com/bid/97632
- https://security.gentoo.org/glsa/201706-12
- https://www.wireshark.org/security/wnpa-sec-2017-16.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13557
