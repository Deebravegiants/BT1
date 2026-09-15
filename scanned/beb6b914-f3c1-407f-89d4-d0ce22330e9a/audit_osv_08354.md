# [M] CVE-2016-2522

## Summary
Severity: Medium
Advisory: CVE-2016-2522
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2522
Type: osv

## Details
The dissect_ber_constrained_bitstring function in epan/dissectors/packet-ber.c in the ASN.1 BER dissector in Wireshark 2.0.x before 2.0.2 does not verify that a certain length is nonzero, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=9b2f3f7c5c9205381cb72e42b66e97d8ed3abf63
- http://www.wireshark.org/security/wnpa-sec-2016-02.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11828
