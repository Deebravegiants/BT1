# [H] Django Vulnerable to Cache Poisoning

## Summary
Severity: High
Advisory: GHSA-rm2j-x595-q9cj
CVE: CVE-2011-4139
CWE: CWE-20, CWE-349
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-rm2j-x595-q9cj
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.2.7
- PyPI: `Django` — affected >=1.3 <1.3.1

## Details
Django before 1.2.7 and 1.3.x before 1.3.1 uses a request's HTTP Host header to construct a full URL in certain circumstances, which allows remote attackers to conduct cache poisoning attacks via a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4139
- https://github.com/django/django/commit/2f7fadc38efa58ac0a8f93f936b82332a199f396
- https://github.com/django/django/commit/c613af4d6485586c79d692b70a9acac429f3ca9d
- https://bugzilla.redhat.com/show_bug.cgi?id=737366
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-4.yaml
- https://hermes.opensuse.org/messages/14700881
- https://www.djangoproject.com/weblog/2011/sep/09
- https://www.djangoproject.com/weblog/2011/sep/10/127
- http://openwall.com/lists/oss-security/2011/09/11/1
- http://openwall.com/lists/oss-security/2011/09/13/2
- http://www.debian.org/security/2011/dsa-2332
