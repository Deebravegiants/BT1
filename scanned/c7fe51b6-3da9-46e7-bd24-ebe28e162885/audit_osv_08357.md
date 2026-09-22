# [M] CVE-2016-2525

## Summary
Severity: Medium
Advisory: CVE-2016-2525
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2525
Type: osv

## Details
epan/dissectors/packet-http2.c in the HTTP/2 dissector in Wireshark 2.0.x before 2.0.2 does not limit the amount of header data, which allows remote attackers to cause a denial of service (memory consumption or application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=6a47ac7624993b99966e1d813245ffb419a2d201
- http://www.wireshark.org/security/wnpa-sec-2016-05.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12077
- https://security.gentoo.org/glsa/201604-05
