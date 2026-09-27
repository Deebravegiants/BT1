# [H] CVE-2018-5336

## Summary
Severity: High
Advisory: CVE-2018-5336
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-11
Source: https://osv.dev/vulnerability/CVE-2018-5336
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.3 and 2.2.0 to 2.2.11, the JSON, XML, NTP, XMPP, and GDB dissectors could crash. This was addressed in epan/tvbparse.c by limiting the recursion depth.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=4f4c95cf46ba6adbd10b09747e10742801bc706b
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=f6702e49a9720d173246668495eece6d77eca5b0
- http://www.securityfocus.com/bid/102504
- https://lists.debian.org/debian-lts-announce/2018/01/msg00032.html
- https://www.debian.org/security/2018/dsa-4101
- https://www.wireshark.org/security/wnpa-sec-2018-01.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14253
