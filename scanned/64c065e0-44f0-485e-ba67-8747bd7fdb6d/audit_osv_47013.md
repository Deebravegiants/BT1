# [M] CVE-2015-8727

## Summary
Severity: Medium
Advisory: CVE-2015-8727
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8727
Type: osv

## Details
The dissect_rsvp_common function in epan/dissectors/packet-rsvp.c in the RSVP dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 does not properly maintain request-key data, which allows remote attackers to cause a denial of service (use-after-free and application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-45.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11793
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=56baca60271379cb97f6a4a6bf72eb526e8b52d0
