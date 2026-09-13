# [H] CVE-2017-5356

## Summary
Severity: High
Advisory: CVE-2017-5356
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2017-5356
Type: osv

## Details
Irssi before 0.8.21 allows remote attackers to cause a denial of service (out-of-bounds read and crash) via a string containing a formatting sequence (%[) without a closing bracket (]).

## References
- http://www.openwall.com/lists/oss-security/2017/01/12/8
- http://www.openwall.com/lists/oss-security/2017/01/13/2
- http://www.securityfocus.com/bid/96581
- https://lists.debian.org/debian-lts-announce/2017/12/msg00022.html
- https://irssi.org/security/irssi_sa_2017_01.txt
- https://blog.fuzzing-project.org/55-Fuzzing-Irssi-with-Perl-Scripts.html
