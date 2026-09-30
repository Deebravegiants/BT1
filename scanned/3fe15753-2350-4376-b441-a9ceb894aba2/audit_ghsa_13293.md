# [H] Django has regular expression denial of service vulnerability in EmailValidator/URLValidator

## Summary
Severity: High
Advisory: GHSA-jh3w-4vvf-mjgr
CVE: CVE-2023-36053
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-03
Source: https://github.com/advisories/GHSA-jh3w-4vvf-mjgr
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.20
- PyPI: `Django` — affected >=4.0a1 <4.1.10
- PyPI: `Django` — affected >=4.2a1 <4.2.3

## Details
In Django 3.2 before 3.2.20, 4 before 4.1.10, and 4.2 before 4.2.3, `EmailValidator` and `URLValidator` are subject to a potential ReDoS (regular expression denial of service) attack via a very large number of domain name labels of emails and URLs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36053
- https://github.com/django/django/commit/454f2fb93437f98917283336201b4048293f7582
- https://github.com/django/django/commit/ad0410ec4f458aa39803e5f6b9a3736527062dcd
- https://github.com/django/django/commit/b7c5feb35a31799de6e582ad6a5a91a9de74e0f9
- https://github.com/django/django/commit/beb3f3d55940d9aa7198bf9d424ab74e873aec3d
- https://www.djangoproject.com/weblog/2023/jul/03/security-releases
- https://www.debian.org/security/2023/dsa-5465
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XG5DYKPNDCEHJQ3TKPJQO7QGSR4FAYMS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NRDGTUN4LTI6HG4TWR3JYLSFVXPZT42A
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQJOMNRMVPCN5WMIZ7YSX5LQ7IR2NY4D
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XG5DYKPNDCEHJQ3TKPJQO7QGSR4FAYMS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NRDGTUN4LTI6HG4TWR3JYLSFVXPZT42A
- https://lists.debian.org/debian-lts-announce/2023/07/msg00022.html
- https://groups.google.com/forum/#%21forum/django-announce
- https://groups.google.com/forum/#!forum/django-announce
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-100.yaml
- https://github.com/django/django
- https://docs.djangoproject.com/en/4.2/releases/security
