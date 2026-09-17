# [M] CVE-2019-12308

## Summary
Severity: Medium
Advisory: CVE-2019-12308
Aliases: GHSA-7rp2-fm2h-wchj, PYSEC-2019-79
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-12308
Type: osv

## Details
An issue was discovered in Django 1.11 before 1.11.21, 2.1 before 2.1.9, and 2.2 before 2.2.2. The clickable Current URL value displayed by the AdminURLFieldWidget displays the provided value without validating it as a safe URL. Thus, an unvalidated value stored in the database, or a value provided as a URL query parameter payload, could result in an clickable JavaScript link.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00025.html
- http://www.securityfocus.com/bid/108559
- https://groups.google.com/forum/#%21topic/django-announce/GEbHU7YoVz8
- https://lists.debian.org/debian-lts-announce/2019/06/msg00001.html
- https://lists.debian.org/debian-lts-announce/2019/07/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/USYRARSYB7PE3S2ZQO7PZNWMH7RPGL5G/
- https://seclists.org/bugtraq/2019/Jul/10
- https://usn.ubuntu.com/4043-1/
- http://www.openwall.com/lists/oss-security/2019/06/03/2
- https://docs.djangoproject.com/en/dev/releases/1.11.21/
- https://docs.djangoproject.com/en/dev/releases/2.1.9/
- https://docs.djangoproject.com/en/dev/releases/2.2.2/
- https://docs.djangoproject.com/en/dev/releases/security/
- https://security.gentoo.org/glsa/202004-17
- https://www.debian.org/security/2019/dsa-4476
- https://www.djangoproject.com/weblog/2019/jun/03/security-releases/
