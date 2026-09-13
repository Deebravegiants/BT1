# [C] CVE-2017-13014

## Summary
Severity: Critical
Advisory: CVE-2017-13014
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-14
Source: https://osv.dev/vulnerability/CVE-2017-13014
Type: osv

## Details
The White Board protocol parser in tcpdump before 4.9.2 has a buffer over-read in print-wb.c:wb_prep(), several functions.

## References
- http://www.securitytracker.com/id/1039307
- https://support.apple.com/HT208221
- http://www.debian.org/security/2017/dsa-3971
- http://www.tcpdump.org/tcpdump-changes.txt
- https://access.redhat.com/errata/RHEA-2018:0705
- https://security.gentoo.org/glsa/201709-23
- https://github.com/the-tcpdump-group/tcpdump/commit/cc356512f512e7fa423b3674db4bb31dbe40ffec
