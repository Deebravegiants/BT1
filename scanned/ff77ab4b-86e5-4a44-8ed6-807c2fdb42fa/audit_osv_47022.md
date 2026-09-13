# [M] CVE-2015-8736

## Summary
Severity: Medium
Advisory: CVE-2015-8736
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-01-04
Source: https://osv.dev/vulnerability/CVE-2015-8736
Type: osv

## Details
The mp2t_find_next_pcr function in wiretap/mp2t.c in the MP2T file parser in Wireshark 2.0.x before 2.0.1 does not reserve memory for a trailer, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) via a crafted file.

## References
- http://www.wireshark.org/security/wnpa-sec-2015-54.html
- https://security.gentoo.org/glsa/201604-05
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11820
- http://www.securityfocus.com/bid/79382
- http://www.securitytracker.com/id/1034551
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=baa3eab78b422616a92ee38551c1b1510dca4ccb
