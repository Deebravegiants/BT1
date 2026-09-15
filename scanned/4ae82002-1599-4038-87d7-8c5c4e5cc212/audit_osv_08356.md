# [M] CVE-2016-2524

## Summary
Severity: Medium
Advisory: CVE-2016-2524
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2524
Type: osv

## Details
epan/dissectors/packet-x509af.c in the X.509AF dissector in Wireshark 2.0.x before 2.0.2 mishandles the algorithm ID, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=5a8020a1b6bb73fcb8bb7eb7d53177bc8a9fc703
- http://www.wireshark.org/security/wnpa-sec-2016-04.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12002
- https://security.gentoo.org/glsa/201604-05
