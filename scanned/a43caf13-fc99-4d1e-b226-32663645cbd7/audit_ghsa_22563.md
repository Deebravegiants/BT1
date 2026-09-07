# [C] Django DNS Rebinding Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3f2c-jm6v-cr35
CVE: CVE-2016-9014
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3f2c-jm6v-cr35
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=1.8a1 <1.8.16
- PyPI: `Django` — affected >=1.9a1 <1.9.11
- PyPI: `Django` — affected >=1.10a1 <1.10.3

## Details
Django before 1.8.x before 1.8.16, 1.9.x before 1.9.11, and 1.10.x before 1.10.3, when settings.DEBUG is True, allow remote attackers to conduct DNS rebinding attacks by leveraging failure to validate the HTTP Host header against settings.ALLOWED_HOSTS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9014
- https://github.com/django/django/commit/45acd6d836895a4c36575f48b3fb36a3dae98d19
- https://github.com/django/django/commit/884e113838e5a72b4b0ec9e5e87aa480f6aa4472
- https://github.com/django/django/commit/c401ae9a7dfb1a94a8a61927ed541d6f93089587
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2016-18.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OG5ROMUPS6C7BXELD3TAUUH7OBYV56WQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QXDKJYHN74BWY3P7AR2UZDVJREQMRE6S
- https://web.archive.org/web/20210123185619/http://www.securityfocus.com/bid/94068
- https://web.archive.org/web/20211204043252/http://www.securitytracker.com/id/1037159
- https://www.djangoproject.com/weblog/2016/nov/01/security-releases
- http://www.debian.org/security/2017/dsa-3835
- http://www.ubuntu.com/usn/USN-3115-1
