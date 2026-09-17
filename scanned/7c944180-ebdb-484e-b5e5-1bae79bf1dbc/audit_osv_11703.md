# [H] CVE-2017-9352

## Summary
Severity: High
Advisory: CVE-2017-9352
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9352
Type: osv

## Details
In Wireshark 2.2.0 to 2.2.6 and 2.0.0 to 2.0.12, the Bazaar dissector could go into an infinite loop. This was addressed in epan/dissectors/packet-bzr.c by ensuring that backwards parsing cannot occur.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=8c5e0cee278ff0678b0ebf4b9c2a614974b4029a
- http://www.securityfocus.com/bid/98804
- http://www.securitytracker.com/id/1038612
- https://www.wireshark.org/security/wnpa-sec-2017-22.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=13599
