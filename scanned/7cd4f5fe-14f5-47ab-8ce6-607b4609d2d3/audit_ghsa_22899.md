# [C] Django Tastypie Improper Deserialization of YAML Data

## Summary
Severity: Critical
Advisory: GHSA-qgvw-qc2q-gv5q
CVE: CVE-2011-4104
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qgvw-qc2q-gv5q
Type: github-advisory

## Affected
- PyPI: `django-tastypie` — affected >=0 <0.9.10

## Details
The `from_yaml` method in serializers.py in Django Tastypie before 0.9.10 does not properly deserialize YAML data, which allows remote attackers to execute arbitrary Python code via vectors related to the yaml.load method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4104
- https://github.com/toastdriven/django-tastypie/commit/e8af315211b07c8f48f32a063233cc3f76dd5bc2
- https://github.com/pypa/advisory-database/tree/main/vulns/django-tastypie/PYSEC-2014-25.yaml
- https://github.com/toastdriven/django-tastypie
- https://groups.google.com/forum/#!topic/django-tastypie/i2aNGDHTUBI
- https://www.djangoproject.com/weblog/2011/nov/01/piston-and-tastypie-security-releases
- http://www.openwall.com/lists/oss-security/2011/11/02/1
- http://www.openwall.com/lists/oss-security/2011/11/02/7
