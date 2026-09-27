# [H] CVE-2017-9372

## Summary
Severity: High
Advisory: CVE-2017-9372
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9372
Type: osv

## Details
PJSIP, as used in Asterisk Open Source 13.x before 13.15.1 and 14.x before 14.4.1, Certified Asterisk 13.13 before 13.13-cert4, and other products, allows remote attackers to cause a denial of service (buffer overflow and application crash) via a SIP packet with a crafted CSeq header in conjunction with a Via header that lacks a branch parameter.

## References
- http://www.securitytracker.com/id/1038529
- http://downloads.asterisk.org/pub/security/AST-2017-002.txt
- http://www.debian.org/security/2017/dsa-3933
- http://www.securityfocus.com/bid/98572
- https://bugs.debian.org/863901
