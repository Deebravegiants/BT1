# [H] CVE-2019-19630

## Summary
Severity: High
Advisory: CVE-2019-19630
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-08
Source: https://osv.dev/vulnerability/CVE-2019-19630
Type: osv

## Details
HTMLDOC 1.9.7 allows a stack-based buffer overflow in the hd_strlcpy() function in string.c (when called from render_contents in ps-pdf.cxx) via a crafted HTML document.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MZLVUBON5AYWYTFTJ4HBSHGTQTY7KBN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FEUT3LG6DWTICKXYAN4SWOQWWCGHPLDJ/
- https://lists.debian.org/debian-lts-announce/2019/12/msg00008.html
- https://lists.debian.org/debian-lts-announce/2021/07/msg00000.html
- https://github.com/michaelrsweet/htmldoc/issues/370
