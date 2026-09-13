# [M] CVE-2016-2526

## Summary
Severity: Medium
Advisory: CVE-2016-2526
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2526
Type: osv

## Details
epan/dissectors/packet-hiqnet.c in the HiQnet dissector in Wireshark 2.0.x before 2.0.2 does not validate the data type, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=69a679cc3a9c087064b7e9521b9e9f3c40dd0b72
- http://www.wireshark.org/security/wnpa-sec-2016-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11983
- https://security.gentoo.org/glsa/201604-05
