# [M] Django Incorrect HTTP detection with reverse-proxy connecting via HTTPS

## Summary
Severity: Medium
Advisory: GHSA-6c7v-2f49-8h26
CVE: CVE-2019-12781
CWE: CWE-319
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-07-03
Source: https://github.com/advisories/GHSA-6c7v-2f49-8h26
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=2.1 <2.1.10
- PyPI: `Django` — affected >=2.2 <2.2.3
- PyPI: `Django` — affected >=1.11 <1.11.22

## Details
An issue was discovered in Django 1.11 before 1.11.22, 2.1 before 2.1.10, and 2.2 before 2.2.3. An HTTP request is not redirected to HTTPS when the SECURE_PROXY_SSL_HEADER and SECURE_SSL_REDIRECT settings are used, and the proxy connects to Django via HTTPS. In other words, django.http.HttpRequest.scheme has incorrect behavior when a client uses HTTP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12781
- https://docs.djangoproject.com/en/dev/releases/security
- https://github.com/advisories/GHSA-6c7v-2f49-8h26
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-10.yaml
- https://groups.google.com/forum/#!topic/django-announce/Is4kLY9ZcZQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5VXXWIOQGXOB7JCGJ3CVUW673LDHKEYL
- https://seclists.org/bugtraq/2019/Jul/10
- https://security.netapp.com/advisory/ntap-20190705-0002
- https://usn.ubuntu.com/4043-1
- https://www.debian.org/security/2019/dsa-4476
- https://www.djangoproject.com/weblog/2019/jul/01/security-releases
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00025.html
- http://www.openwall.com/lists/oss-security/2019/07/01/3
