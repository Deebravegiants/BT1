# [H] CVE-2017-7702

## Summary
Severity: High
Advisory: CVE-2017-7702
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-7702
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.5 and 2.0.0 to 2.0.11, the WBXML dissector could go into an infinite loop, triggered by packet injection or a malformed capture file. This was addressed in epan/dissectors/packet-wbxml.c by adding length validation.

## References
- http://www.securitytracker.com/id/1038262
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2f322f66cbcca2fefdaa630494f9d6c97eb659b7
- http://www.securityfocus.com/bid/97633
- https://security.gentoo.org/glsa/201706-12
- https://www.wireshark.org/security/wnpa-sec-2017-13.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13477
