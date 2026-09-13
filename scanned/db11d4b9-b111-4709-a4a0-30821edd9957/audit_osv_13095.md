# [H] CVE-2018-17407

## Summary
Severity: High
Advisory: CVE-2018-17407
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-23
Source: https://osv.dev/vulnerability/CVE-2018-17407
Type: osv

## Details
An issue was discovered in t1_check_unusual_charstring functions in writet1.c files in TeX Live before 2018-09-21. A buffer overflow in the handling of Type 1 fonts allows arbitrary code execution when a malicious font is loaded by one of the vulnerable tools: pdflatex, pdftex, dvips, or luatex.

## References
- https://lists.debian.org/debian-security-announce/2018/msg00230.html
- https://usn.ubuntu.com/3788-1/
- https://usn.ubuntu.com/3788-2/
- https://www.debian.org/security/2018/dsa-4299
- https://github.com/TeX-Live/texlive-source/commit/6ed0077520e2b0da1fd060c7f88db7b2e6068e4c
