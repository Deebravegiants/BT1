# [M] CVE-2015-8722

## Summary
Severity: Medium
Advisory: CVE-2015-8722
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8722
Type: osv

## Details
epan/dissectors/packet-sctp.c in the SCTP dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 does not validate the frame pointer, which allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-41.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11767
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79814
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=1b32d505a59475d51d9b2bed5f0869d2d154e8b6
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2259bf8a827088081bef101f98e4983de8aa8099
