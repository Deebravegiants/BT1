# [M] CVE-2015-8721

## Summary
Severity: Medium
Advisory: CVE-2015-8721
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8721
Type: osv

## Details
Buffer overflow in the tvb_uncompress function in epan/tvbuff_zlib.c in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 allows remote attackers to cause a denial of service (application crash) via a crafted packet with zlib compression.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-40.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11548
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79814
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=cec0593ae6c3bca65eff65741c2a10f3de3e0afe
