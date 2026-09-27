# [M] CVE-2015-8739

## Summary
Severity: Medium
Advisory: CVE-2015-8739
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8739
Type: osv

## Details
The ipmi_fmt_udpport function in epan/dissectors/packet-ipmi.c in the IPMI dissector in Wireshark 2.0.x before 2.0.1 improperly attempts to access a packet scope, which allows remote attackers to cause a denial of service (assertion failure and application exit) via a crafted packet.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-57.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11831
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=96bf82ced0b58c7a4c2a6c300efeebe4f05c0ff4
