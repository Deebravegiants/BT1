# [H] CVE-2017-12990

## Summary
Severity: High
Advisory: CVE-2017-12990
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-14
Source: https://osv.dev/vulnerability/CVE-2017-12990
Type: osv

## Details
The ISAKMP parser in tcpdump before 4.9.2 could enter an infinite loop due to bugs in print-isakmp.c, several functions.

## References
- http://www.securitytracker.com/id/1039307
- https://support.apple.com/HT208221
- http://www.debian.org/security/2017/dsa-3971
- http://www.tcpdump.org/tcpdump-changes.txt
- https://access.redhat.com/errata/RHEA-2018:0705
- https://security.gentoo.org/glsa/201709-23
- https://github.com/the-tcpdump-group/tcpdump/commit/c2ef693866beae071a24b45c49f9674af1df4028
