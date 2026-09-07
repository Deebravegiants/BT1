# [H] Django contains Uncontrolled Resource Consumption via cached header

## Summary
Severity: High
Advisory: GHSA-q2jf-h9jm-m7p4
CVE: CVE-2023-23969
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-q2jf-h9jm-m7p4
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=3.2a1 <3.2.17
- PyPI: `Django` — affected >=4.0a1 <4.0.9
- PyPI: `Django` — affected >=4.1a1 <4.1.6

## Details
In Django 3.2 before 3.2.17, 4.0 before 4.0.9, and 4.1 before 4.1.6, the parsed values of Accept-Language headers are cached in order to avoid repetitive parsing. This leads to a potential denial-of-service vector via excessive memory usage if the raw value of Accept-Language headers is very large.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-23969
- https://github.com/django/django/commit/4452642f193533e288a52c02efb5bbc766a68f95
- https://github.com/django/django/commit/9d7bd5a56b1ce0576e8e07a8001373576d277942
- https://github.com/django/django/commit/c7e0151fdf33e1b11d488b6f67b94fdf3a30614a
- https://docs.djangoproject.com/en/4.1/releases/security
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2023-12.yaml
- https://groups.google.com/forum/#!forum/django-announce
- https://lists.debian.org/debian-lts-announce/2023/02/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWY6DQWRVBALV73BPUVBXC3QIYUM24IK
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LTZVAKU5ALQWOKFTPISE257VCVIYGFQI
- https://security.netapp.com/advisory/ntap-20230302-0007
- https://www.djangoproject.com/weblog/2023/feb/01/security-releases
