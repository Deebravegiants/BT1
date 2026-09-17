# [H] Denial of service in django

## Summary
Severity: High
Advisory: GHSA-3jqw-crqj-w8qw
CVE: CVE-2011-4137
CWE: CWE-1088
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-3jqw-crqj-w8qw
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.2.7
- PyPI: `Django` — affected >=1.3 <1.3.1

## Details
The verify_exists functionality in the URLField implementation in Django before 1.2.7 and 1.3.x before 1.3.1 relies on Python libraries that attempt access to an arbitrary URL with no timeout, which allows remote attackers to cause a denial of service (resource consumption) via a URL associated with (1) a slow response, (2) a completed TCP connection with no application data sent, or (3) a large amount of application data, a related issue to CVE-2011-1521.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4137
- https://github.com/django/django/commit/1a76dbefdfc60e2d5954c0ba614c3d054ba9c3f0
- https://github.com/django/django/commit/7268f8af86186518821d775c530d5558fd726930
- https://bugzilla.redhat.com/show_bug.cgi?id=737366
- https://github.com/advisories/GHSA-3jqw-crqj-w8qw
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-2.yaml
- https://hermes.opensuse.org/messages/14700881
- https://www.djangoproject.com/weblog/2011/sep/09
- https://www.djangoproject.com/weblog/2011/sep/10/127
- http://openwall.com/lists/oss-security/2011/09/11/1
- http://openwall.com/lists/oss-security/2011/09/13/2
- http://openwall.com/lists/oss-security/2011/09/15/5
- http://www.debian.org/security/2011/dsa-2332
