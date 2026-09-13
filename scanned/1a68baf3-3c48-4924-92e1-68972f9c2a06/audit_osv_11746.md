# [H] CVE-2017-9468

## Summary
Severity: High
Advisory: CVE-2017-9468
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-07
Source: https://osv.dev/vulnerability/CVE-2017-9468
Type: osv

## Details
In Irssi before 1.0.3, when receiving a DCC message without source nick/host, it attempts to dereference a NULL pointer. Thus, remote IRC servers can cause a crash.

## References
- http://www.debian.org/security/2017/dsa-3885
- http://www.securityfocus.com/bid/99015
- http://www.securitytracker.com/id/1038621
- http://openwall.com/lists/oss-security/2017/06/06/4
- https://irssi.org/security/irssi_sa_2017_06.txt
