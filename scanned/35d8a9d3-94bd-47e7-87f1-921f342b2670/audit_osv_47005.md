# [M] CVE-2015-8719

## Summary
Severity: Medium
Advisory: CVE-2015-8719
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8719
Type: osv

## Details
The dissect_dns_answer function in epan/dissectors/packet-dns.c in the DNS dissector in Wireshark 1.12.x before 1.12.9 mishandles the EDNS0 Client Subnet option, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-38.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=10988
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79816
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=30651ab18b42e666f57ea239e58f3ff3a5e9c4ad
