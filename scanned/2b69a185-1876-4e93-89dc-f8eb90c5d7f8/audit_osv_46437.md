# [C] CVE-2010-4344

## Summary
Severity: Critical
Advisory: CVE-2010-4344
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2010-12-14
Source: https://osv.dev/vulnerability/CVE-2010-4344
Type: osv

## Details
Heap-based buffer overflow in the string_vformat function in string.c in Exim before 4.70 allows remote attackers to execute arbitrary code via an SMTP session that includes two MAIL commands in conjunction with a large message containing crafted headers, leading to improper rejection logging.

## References
- http://lists.opensuse.org/opensuse-security-announce/2010-12/msg00003.html
- http://openwall.com/lists/oss-security/2010/12/10/1
- http://secunia.com/advisories/40019
- http://secunia.com/advisories/42576
- http://secunia.com/advisories/42586
- http://secunia.com/advisories/42587
- http://secunia.com/advisories/42589
- http://www.debian.org/security/2010/dsa-2131
- http://www.kb.cert.org/vuls/id/682457
- http://www.metasploit.com/modules/exploit/unix/smtp/exim4_string_format
- http://www.securityfocus.com/archive/1/515172/100/0/threaded
- http://www.securityfocus.com/bid/45308
- http://www.securitytracker.com/id?1024858
- http://www.ubuntu.com/usn/USN-1032-1
- http://www.vupen.com/english/advisories/2010/3171
- http://www.vupen.com/english/advisories/2010/3172
- http://www.vupen.com/english/advisories/2010/3181
- http://www.vupen.com/english/advisories/2010/3186
- http://www.vupen.com/english/advisories/2010/3204
- http://www.vupen.com/english/advisories/2010/3246
