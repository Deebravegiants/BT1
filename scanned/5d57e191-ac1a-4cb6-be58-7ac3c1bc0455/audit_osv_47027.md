# [M] CVE-2015-8741

## Summary
Severity: Medium
Advisory: CVE-2015-8741
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8741
Type: osv

## Details
The dissect_ppi function in epan/dissectors/packet-ppi.c in the PPI dissector in Wireshark 2.0.x before 2.0.1 does not initialize a packet-header data structure, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-59.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11876
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=2290eba5cb25f927f9142680193ac1158d35506e
