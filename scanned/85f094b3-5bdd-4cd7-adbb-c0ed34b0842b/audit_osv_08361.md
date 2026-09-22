# [M] CVE-2016-2529

## Summary
Severity: Medium
Advisory: CVE-2016-2529
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2529
Type: osv

## Details
The iseries_check_file_type function in wiretap/iseries.c in the iSeries file parser in Wireshark 2.0.x before 2.0.2 does not consider that a line may lack the "OBJECT PROTOCOL" substring, which allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted file.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=96d585a5e9baef21e1eea8505d78305b034dc80e
- http://www.wireshark.org/security/wnpa-sec-2016-09.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11985
- https://security.gentoo.org/glsa/201604-05
