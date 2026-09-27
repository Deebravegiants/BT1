# [M] CVE-2018-7537

## Summary
Severity: Medium
Advisory: CVE-2018-7537
Aliases: GHSA-2f9x-5v75-3qv4, PYSEC-2018-6
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-03-09
Source: https://osv.dev/vulnerability/CVE-2018-7537
Type: osv

## Details
An issue was discovered in Django 2.0 before 2.0.3, 1.11 before 1.11.11, and 1.8 before 1.8.19. If django.utils.text.Truncator's chars() and words() methods were passed the html=True argument, they were extremely slow to evaluate certain inputs due to a catastrophic backtracking vulnerability in a regular expression. The chars() and words() methods are used to implement the truncatechars_html and truncatewords_html template filters, which were thus vulnerable.

## References
- http://www.securityfocus.com/bid/103357
- https://access.redhat.com/errata/RHSA-2018:2927
- https://access.redhat.com/errata/RHSA-2019:0265
- https://lists.debian.org/debian-lts-announce/2018/03/msg00006.html
- https://usn.ubuntu.com/3591-1/
- https://www.debian.org/security/2018/dsa-4161
- https://www.djangoproject.com/weblog/2018/mar/06/security-releases/
