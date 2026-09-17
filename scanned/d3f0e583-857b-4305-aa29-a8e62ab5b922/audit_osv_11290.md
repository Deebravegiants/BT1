# [H] CVE-2017-7227

## Summary
Severity: High
Advisory: CVE-2017-7227
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-22
Source: https://osv.dev/vulnerability/CVE-2017-7227
Type: osv

## Details
GNU linker (ld) in GNU Binutils 2.28 is vulnerable to a heap-based buffer overflow while processing a bogus input script, leading to a program crash. This relates to lack of '\0' termination of a name field in ldlex.l.

## References
- http://www.securityfocus.com/bid/97209
- https://security.gentoo.org/glsa/201801-01
- https://sourceware.org/bugzilla/show_bug.cgi?id=20906
