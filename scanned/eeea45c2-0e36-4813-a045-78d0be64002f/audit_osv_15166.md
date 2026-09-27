# [H] CVE-2019-14232

## Summary
Severity: High
Advisory: CVE-2019-14232
Aliases: GHSA-c4qh-4vgv-qc6g, PYSEC-2019-11
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-02
Source: https://osv.dev/vulnerability/CVE-2019-14232
Type: osv

## Details
An issue was discovered in Django 1.11.x before 1.11.23, 2.1.x before 2.1.11, and 2.2.x before 2.2.4. If django.utils.text.Truncator's chars() and words() methods were passed the html=True argument, they were extremely slow to evaluate certain inputs due to a catastrophic backtracking vulnerability in a regular expression. The chars() and words() methods are used to implement the truncatechars_html and truncatewords_html template filters, which were thus vulnerable.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00025.html
- http://www.openwall.com/lists/oss-security/2023/10/04/6
- http://www.openwall.com/lists/oss-security/2024/03/04/1
- https://groups.google.com/forum/#%21topic/django-announce/jIoju2-KLDs
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/STVX7X7IDWAH5SKE6MBMY3TEI6ZODBTK/
- https://seclists.org/bugtraq/2019/Aug/15
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00006.html
- https://security.gentoo.org/glsa/202004-17
- https://security.netapp.com/advisory/ntap-20190828-0002/
- https://www.debian.org/security/2019/dsa-4498
- https://www.djangoproject.com/weblog/2019/aug/01/security-releases/
- https://docs.djangoproject.com/en/dev/releases/security/
