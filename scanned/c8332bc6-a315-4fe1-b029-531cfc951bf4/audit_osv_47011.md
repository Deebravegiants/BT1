# [M] CVE-2015-8725

## Summary
Severity: Medium
Advisory: CVE-2015-8725
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8725
Type: osv

## Details
The dissect_diameter_base_framed_ipv6_prefix function in epan/dissectors/packet-diameter.c in the DIAMETER dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 does not validate the IPv6 prefix length, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3505
- http://www.wireshark.org/security/wnpa-sec-2015-43.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11792
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=aaa28a9d39158ca1033bbd3372cf423abbf4f202
