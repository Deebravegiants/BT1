# [M] CVE-2015-8715

## Summary
Severity: Medium
Advisory: CVE-2015-8715
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8715
Type: osv

## Details
epan/dissectors/packet-alljoyn.c in the AllJoyn dissector in Wireshark 1.12.x before 1.12.9 does not check for empty arguments, which allows remote attackers to cause a denial of service (infinite loop) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-34.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11607
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79816
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=40caff2d1fb08262c84aaaa8ac584baa8866dd7c
