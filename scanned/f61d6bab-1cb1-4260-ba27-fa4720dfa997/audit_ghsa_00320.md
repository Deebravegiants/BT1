# [C] Django-piston and Django-tastypie do not properly deserialize YAML data

## Summary
Severity: Critical
Advisory: GHSA-pvhp-v9qp-xf5r
CVE: CVE-2011-4103
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-pvhp-v9qp-xf5r
Type: github-advisory

## Affected
- PyPI: `django-piston` — affected >=0.2.0 <0.2.2.1

## Details
emitters.py in Django Piston before 0.2.3 and 0.2.x before 0.2.2.1 does not properly deserialize YAML data, which allows remote attackers to execute arbitrary Python code via vectors related to the yaml.load method.

Django Tastypie has a very similar vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4103
- https://bitbucket.org/jespern/django-piston
- https://bitbucket.org/jespern/django-piston/commits/91bdaec89543
- https://bugzilla.redhat.com/show_bug.cgi?id=750658
- https://github.com/advisories/GHSA-pvhp-v9qp-xf5r
- https://github.com/pypa/advisory-database/tree/main/vulns/django-piston/PYSEC-2014-24.yaml
- https://www.djangoproject.com/weblog/2011/nov/01/piston-and-tastypie-security-releases
- http://www.debian.org/security/2011/dsa-2344
- http://www.openwall.com/lists/oss-security/2011/11/01/10
