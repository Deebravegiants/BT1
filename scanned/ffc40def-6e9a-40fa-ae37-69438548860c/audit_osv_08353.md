# [H] CVE-2016-2521

## Summary
Severity: High
Advisory: CVE-2016-2521
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-28
Source: https://osv.dev/vulnerability/CVE-2016-2521
Type: osv

## Details
Untrusted search path vulnerability in the WiresharkApplication class in ui/qt/wireshark_application.cpp in Wireshark 1.12.x before 1.12.10 and 2.0.x before 2.0.2 on Windows allows local users to gain privileges via a Trojan horse riched20.dll.dll file in the current working directory, related to use of QLibrary.

## References
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securitytracker.com/id/1035118
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4a79cf2e1ab056faaddd252aa56520435b318a56
- http://www.wireshark.org/security/wnpa-sec-2016-01.html
- https://security.gentoo.org/glsa/201604-05
