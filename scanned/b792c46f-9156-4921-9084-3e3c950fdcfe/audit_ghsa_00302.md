# [M] Session manipulation in Django

## Summary
Severity: Medium
Advisory: GHSA-x88j-93vc-wpmp
CVE: CVE-2011-4136
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-x88j-93vc-wpmp
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.2.7
- PyPI: `Django` — affected >=1.3 <1.3.1

## Details
django.contrib.sessions in Django before 1.2.7 and 1.3.x before 1.3.1, when session data is stored in the cache, uses the root namespace for both session identifiers and application-data keys, which allows remote attackers to modify a session by triggering use of a key that is equal to that session's identifier.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4136
- https://github.com/django/django/commit/ac7c3a110f906e4dfed3a17451bf7fd9fcb81296
- https://github.com/django/django/commit/fbe2eead2fa9d808658ca582241bcacb02618840
- https://bugzilla.redhat.com/show_bug.cgi?id=737366
- https://github.com/advisories/GHSA-x88j-93vc-wpmp
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2011-1.yaml
- https://hermes.opensuse.org/messages/14700881
- https://www.djangoproject.com/weblog/2011/sep/09
- https://www.djangoproject.com/weblog/2011/sep/10/127
- http://openwall.com/lists/oss-security/2011/09/11/1
- http://openwall.com/lists/oss-security/2011/09/13/2
- http://www.debian.org/security/2011/dsa-2332
