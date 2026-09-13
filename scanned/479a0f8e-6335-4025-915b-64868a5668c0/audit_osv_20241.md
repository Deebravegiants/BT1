# [H] CVE-2021-32558

## Summary
Severity: High
Advisory: CVE-2021-32558
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-32558
Type: osv

## Details
An issue was discovered in Sangoma Asterisk 13.x before 13.38.3, 16.x before 16.19.1, 17.x before 17.9.4, and 18.x before 18.5.1, and Certified Asterisk before 16.8-cert10. If the IAX2 channel driver receives a packet that contains an unsupported media format, a crash can occur.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00005.html
- https://www.debian.org/security/2021/dsa-4999
- http://packetstormsecurity.com/files/163639/Asterisk-Project-Security-Advisory-AST-2021-008.html
- http://seclists.org/fulldisclosure/2021/Jul/49
- https://downloads.asterisk.org/pub/security/AST-2021-008.html
- https://issues.asterisk.org/jira/browse/ASTERISK-29392
