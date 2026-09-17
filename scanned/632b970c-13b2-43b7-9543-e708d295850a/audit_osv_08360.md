# [M] CVE-2016-2528

## Summary
Severity: Medium
Advisory: CVE-2016-2528
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2528
Type: osv

## Details
The dissect_nhdr_extopt function in epan/dissectors/packet-lbmc.c in the LBMC dissector in Wireshark 2.0.x before 2.0.2 does not validate length values, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1c090e929269a78bf7a4cb3dc0d34565f4351312
- http://www.wireshark.org/security/wnpa-sec-2016-08.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11984
- https://security.gentoo.org/glsa/201604-05
