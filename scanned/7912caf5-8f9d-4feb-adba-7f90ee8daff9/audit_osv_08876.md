# [M] CVE-2016-6513

## Summary
Severity: Medium
Advisory: CVE-2016-6513
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-6513
Type: osv

## Details
epan/dissectors/packet-wbxml.c in the WBXML dissector in Wireshark 2.x before 2.0.5 does not restrict the recursion depth, which allows remote attackers to cause a denial of service (application crash) via a crafted packet.

## References
- http://www.securitytracker.com/id/1036480
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=347f071f1b9180563c28b0f3d0627b91eb456c72
- http://www.wireshark.org/security/wnpa-sec-2016-49.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=12663
- http://openwall.com/lists/oss-security/2016/07/28/3
