# [H] CVE-2018-16140

## Summary
Severity: High
Advisory: CVE-2018-16140
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-08-30
Source: https://osv.dev/vulnerability/CVE-2018-16140
Type: osv

## Details
A buffer underwrite vulnerability in get_line() (read.c) in fig2dev 3.2.7a allows an attacker to write prior to the beginning of the buffer via a crafted .fig file.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00018.html
- https://usn.ubuntu.com/3760-1/
- https://sourceforge.net/p/mcj/tickets/28/
