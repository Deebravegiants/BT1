# [M] CVE-2015-8731

## Summary
Severity: Medium
Advisory: CVE-2015-8731
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8731
Type: osv

## Details
The dissct_rsl_ipaccess_msg function in epan/dissectors/packet-rsl.c in the RSL dissector in Wireshark 1.12.x before 1.12.9 and 2.0.x before 2.0.1 does not reject unknown TLV types, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet.

## References
- http://www.debian.org/security/2016/dsa-3516
- http://www.wireshark.org/security/wnpa-sec-2015-49.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11829
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2930d3105c3ff2bfb1278b34ad10e2e71c3b8fb0
