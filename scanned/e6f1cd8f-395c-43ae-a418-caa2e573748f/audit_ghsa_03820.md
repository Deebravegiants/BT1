# [H] Django Denial-of-service by filling session store

## Summary
Severity: High
Advisory: GHSA-h582-2pch-3xv3
CVE: CVE-2015-5143
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-h582-2pch-3xv3
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.4.21
- PyPI: `Django` — affected >=1.5 <1.7.9
- PyPI: `Django` — affected >=1.8 <1.8.3

## Details
The session backends in Django before 1.4.21, 1.5.x through 1.6.x, 1.7.x before 1.7.9, and 1.8.x before 1.8.3 allows remote attackers to cause a denial of service (session store consumption) via multiple requests with unique session keys.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5143
- https://github.com/django/django/commit/1828f4341ec53a8684112d24031b767eba557663
- https://github.com/django/django/commit/2e47f3e401c29bc2ba5ab794d483cb0820855fb9
- https://github.com/django/django/commit/66d12d1ababa8f062857ee5eb43276493720bf16
- https://github.com/advisories/GHSA-h582-2pch-3xv3
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2015-20.yaml
- https://security.gentoo.org/glsa/201510-06
- https://www.djangoproject.com/weblog/2015/jul/08/security-releases
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172084.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00043.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00046.html
- http://rhn.redhat.com/errata/RHSA-2015-1678.html
- http://rhn.redhat.com/errata/RHSA-2015-1686.html
- http://www.debian.org/security/2015/dsa-3305
- http://www.oracle.com/technetwork/topics/security/bulletinoct2015-2511968.html
- http://www.ubuntu.com/usn/USN-2671-1
