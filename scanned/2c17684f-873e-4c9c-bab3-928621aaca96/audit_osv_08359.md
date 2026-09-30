# [M] CVE-2016-2527

## Summary
Severity: Medium
Advisory: CVE-2016-2527
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2527
Type: osv

## Details
wiretap/nettrace_3gpp_32_423.c in the 3GPP TS 32.423 Trace file parser in Wireshark 2.0.x before 2.0.2 does not ensure that a '\0' character is present at the end of certain strings, which allows remote attackers to cause a denial of service (stack-based buffer overflow and application crash) via a crafted file.

## References
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=140aad08e081489b5cdb715cb5bca01db856fded
- http://www.wireshark.org/security/wnpa-sec-2016-07.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11982
- https://security.gentoo.org/glsa/201604-05
