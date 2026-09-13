# [M] CVE-2015-8737

## Summary
Severity: Medium
Advisory: CVE-2015-8737
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8737
Type: osv

## Details
The mp2t_open function in wiretap/mp2t.c in the MP2T file parser in Wireshark 2.0.x before 2.0.1 does not validate the bit rate, which allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted file.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-55.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11821
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=e3fc691368af60bbbaec9e038ee6a6d3b7707955
