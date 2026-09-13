# [H] CVE-2018-11360

## Summary
Severity: High
Advisory: CVE-2018-11360
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-22
Source: https://osv.dev/vulnerability/CVE-2018-11360
Type: osv

## Details
In Wireshark 2.6.0, 2.4.0 to 2.4.6, and 2.2.0 to 2.2.14, the GSM A DTAP dissector could crash. This was addressed in epan/dissectors/packet-gsm_a_dtap.c by fixing an off-by-one error that caused a buffer overflow.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=a55b36c51f83a7b9680824e8ee3a6ce8429ab24b
- http://www.securityfocus.com/bid/104308
- http://www.securitytracker.com/id/1041036
- https://www.debian.org/security/2018/dsa-4217
- https://www.wireshark.org/security/wnpa-sec-2018-30.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14688
