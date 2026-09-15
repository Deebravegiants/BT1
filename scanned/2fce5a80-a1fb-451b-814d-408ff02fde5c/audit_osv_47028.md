# [M] CVE-2015-8742

## Summary
Severity: Medium
Advisory: CVE-2015-8742
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8742
Type: osv

## Details
The dissect_CPMSetBindings function in epan/dissectors/packet-mswsp.c in the MS-WSP dissector in Wireshark 2.0.x before 2.0.1 does not validate the column size, which allows remote attackers to cause a denial of service (memory consumption or application crash) via a crafted packet.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-60.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11931
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=d48b0eff28c995947ac3f8d842ddd9b50dd5798d
